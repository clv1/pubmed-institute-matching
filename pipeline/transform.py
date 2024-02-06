# pylint: disable = invalid-name, line-too-long
"""Transform script."""

import re
import csv
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import spacy
import geonamescache
from rapidfuzz.distance import Levenshtein


PUBMED_DATA = './input_data/pubmed_data.xml'
SAMPLE_PUBMED_DATA = './input_data/sample_data.xml'

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(\.[a-zA-Z]+)+')
UK = r'[a-zA-Z]{1,2}[0-9]{1,2}[a-zA-Z0-9]* [0-9][a-zA-Z]{2}'
US = r'\s\d{5}-\d{4}'
CAN = r'[a-zA-Z][0-9][a-zA-Z] [0-9][a-zA-Z][0-9]'
POSTCODE_REGEX = re.compile(f'({UK}|{US}|{CAN})')

# Load the spacy model with unnecessary components disabled
nlp = spacy.load("en_core_web_sm", disable=["parser", "textcat"])


def parse_xml(file_path: str) -> ET.Element:
    """Parses the xml file and returns an element object."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root


def extract_article_details(article_element: ET.Element) -> dict:
    """
    Extracts certain fields for a given article.
    Returns them in a dictionary.
    """
    article_citation = article_element.find('.//MedlineCitation')

    title = article_citation.find('.//ArticleTitle').text
    pmid = article_citation.find('.//PMID').text
    year = article_citation.find('.//Year').text

    keywords = article_citation.iterfind(
        './KeywordList/Keyword')
    keywords_list = [keyword.text for keyword in keywords]

    mesh_headings = article_citation.iterfind(
        './MeshHeadingList/MeshHeading')
    mesh_descriptor_ids = [mesh_heading.find(
        "./DescriptorName").attrib['UI'] for mesh_heading in mesh_headings]

    extracted_fields = {'title': title, 'year': year, 'pmid': pmid,
                        'keywords_list': keywords_list, 'mesh_ids': mesh_descriptor_ids}

    return extracted_fields


def extract_author_details(author_element: ET.Element) -> dict:
    """
    Extracts certain fields for a given author.
    Returns them in a dictionary.
    """
    forename = author_element.find(
        './/ForeName').text if author_element.find('.//ForeName') is not None else np.nan
    lastname = author_element.find(
        './/LastName').text if author_element.find('.//LastName') is not None else np.nan
    initials = author_element.find(
        './/Initials').text if author_element.find('.//Initials') is not None else np.nan
    reported_identifier = author_element.find(
        './/Identifier[@Source="GRID"]').text if author_element.find(
        './/Identifier[@Source="GRID"]') is not None else np.nan

    affiliation_list = [affiliation.text for affiliation in author_element.iterfind(
        './/AffiliationInfo/Affiliation')]

    email, postcode, country, reported_institution = np.nan, np.nan, np.nan, None

    for affiliation_text in affiliation_list:
        match_email = re.search(EMAIL_REGEX, affiliation_text)
        if match_email:
            email = match_email.group()

        match_postcode = re.search(POSTCODE_REGEX, affiliation_text)
        if match_postcode:
            postcode = match_postcode.group()

        country = extract_country_from_affiliation_text(affiliation_text)
        reported_institution = extract_institution_details_from_affiliation_text(
            affiliation_text)

    if reported_institution is None:
        proper_institution_details = {'name': np.nan, 'grid_id': np.nan}
    else:
        proper_institution_details = match_institution_details_on_name(
            reported_institution)

    author_details = {
        'forename': forename,
        'lastname': lastname,
        'initials': initials,
        'reported_identity': reported_identifier,
        'proper_identity': proper_institution_details['grid_id'],
        'reported_institution': reported_institution,
        'proper_institution': proper_institution_details['name'],
        'email': email,
        'postcode': postcode,
        'country': country,
        'affiliations': affiliation_list,
    }

    return author_details


def assemble_articles_df(xml_root: ET.ElementTree) -> list[dict]:
    """
    Takes in xml data as an ElementTree root.
    Extracts the details of each author.
    Returns them as a list.
    """
    articles_list = []

    for article in xml_root.iterfind('.//PubmedArticle'):

        for author in article.iterfind('.//AuthorList/Author'):

            author_details = extract_author_details(author)
            article_details = extract_article_details(article)
            article_details.update(author_details)
            articles_list.append(article_details)

    df = pd.DataFrame(articles_list)
    return df.explode('affiliations') if 'affiliations' in df.columns else df


# ----- SUPPORT FUNCTIONS ----- #

def get_gnc_countries() -> set:
    """
    Uses the geonamescache Python library to retrieve countries.
    Returns a set of country names.
    """
    # gets nested dictionary for countries
    gnc_dict = geonamescache.GeonamesCache().get_countries()
    # returns a set of country names
    return {country_dict['name'] for country_dict in gnc_dict.values()}


def extract_country_from_affiliation_text(affiliation_text: str) -> str:
    """
    Takes in a single affiliation.
    Returns a country if its name is contained within the affiliation text.
    """
    doc = nlp(affiliation_text)
    countries = get_gnc_countries()

    for entity in doc.ents:
        if entity.label_ == "GPE" and entity.text in countries:
            return entity.text

    return np.nan


def extract_institution_details_from_affiliation_text(affiliation_text: str) -> set:
    """
    Takes in a single affiliation.
    Returns a set of institutions if their names are contained within the affiliation text.
    """
    doc = nlp(affiliation_text)
    institutions = {
        entity.text for entity in doc.ents if entity.label_ == "ORG"}
    return institutions if institutions else None


def load_grid_institutes() -> set:
    """
    Loads the GRID institute data as a list of dictionaries.
    """
    with open("./input_data/grid_data/grid_institutes.csv", encoding="utf_8") as file:
        grid_institute_dicts = csv.DictReader(file)
        return {institute['name']: institute['grid_id'] for institute in grid_institute_dicts}
GRID_INSTITUTE_DATA = load_grid_institutes()


def match_institution_details_on_name(institution_elements: list[str]) -> str:
    """
    Takes in an institution's elements as input.
    Attempts to fuzzy match elements with grid data institutes by similarity.
    Returns details of matched institute.
    """
    if institution_elements:
        matches = []

        for element in institution_elements:

            for name, grid_id in GRID_INSTITUTE_DATA.items():
                similarity = Levenshtein.normalized_similarity(name, element)
                if similarity > 0.90:
                    matches.append(
                        {'name': name, 'grid_id': grid_id, 'similarity': similarity})
                    break  # exit early
        if matches:
            return max(matches, key=lambda match: match['similarity'])

    return {'grid_id': np.nan, 'name': np.nan}
