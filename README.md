[![badge](./.github/badges/code_quality.svg)](./code_review/report.json)
[![badge](./.github/badges/total_errors.svg)](./code_review/report.json)


# Pubmed Institute Matching
# (🚧 Under construction 🚧)

---

# Problem

A client from the pharmaceutical industry need to track all published research on a particular topic as part of their R&D efforts. They need to collate and analyse research papers from various research institutions to understand a given disease comprehensively and develop new and effective treatments.

This approach of collecting and analysing research papers from various sources is a commonly used method in the pharmaceutical industry to advance understanding of a particular disease or condition. By combining the findings from different research studies, a pharmaceutical company can gain a complete picture of a disease, including its causes, symptoms, and potential treatments.

By leveraging its expertise and resources, PharmaZer could expand its focus to other diseases and conditions, such as cancer, cardiovascular disease, or neurological disorders. The company would follow a similar process, collecting research papers and other relevant information from various sources to gain a comprehensive understanding of the disease in question.

By leveraging its expertise and resources, PharmaZer could expand its focus to other diseases and conditions, such as cancer, cardiovascular disease, or neurological disorders. The company would follow a similar process, collecting research papers and other relevant information from various sources to gain a comprehensive understanding of the disease in question.

This information would then be used to develop new and innovative treatments that are safe and effective. By continuously expanding its focus to other diseases, PharmaZer could become a leading player in the pharmaceutical industry and help to bring new treatments to patients more quickly.

## Task

One of the challenges that PharmaZer may face when collating research papers from various sources is the issue of inconsistent naming of organisations. This can occur when the same organisation is referred to by different names in different papers, making it difficult to accurately match and collate the data.

For example, some publications might include

> Harvard University

while others might include

> Harvard Medical School

however both of them refer to essentially the same medical institution.

This inconsistency in naming can also have an impact on the results of data analysis, as it can lead to errors in data aggregation and hinder the ability to accurately compare the findings of different studies.

To address this challenge, we will need to implement a system to standardize the naming of organizations and institutions. This could involve manually reviewing the research papers to identify and standardize the names of organizations, or using data-driven techniques such as natural language processing or machine learning to automate this process.

By addressing this issue of inconsistent naming, PharmaZer can ensure that the research papers are accurately collated and that the results of the data analysis are reliable and trustworthy.

Our client - PharmaZer - have approached us to help them solve this problem all while making using of the PubMed database which contains medical research as well as information about institutions of locations.

## Project Solution

Eve heads the Immunology team at PharmaZer, acting not just as a lead researcher on key projects but also being responsible for the smooth running of the department, ensuring that work is as streamlined, organised, and cost-effective as possible.

While Eve's short-term focus is collating research on Sjogren Syndrome, she'd ideally like to use the same techniques on other research areas in the future. A low-cost, repeatable tool that allows non-technical staff to quickly collate and organise research data on any topic would be of huge benefit to her work.

The client has given us a dataset named PubMed which contains lists of published medical journals. Apart from the PubMed dataset, we also have access to the Global Research Identifier Database (GRID) datasets which contains the standard names and alias of multiple medical institutions. We can use the standardised GRID dataset to identify all the multiple occurrences of certain institutions with the PubMed Articles correctly.

The project's final goal is to match the names of the institutions in the PubMed dataset to the 'source of truth' in the GRID datasets.

This is essentially a 'record linkage' (aka 'data matching' or 'entity resolution') problem.

### Inputs

We will be working with (and matching across) two datasets:

1. Data retrieved from the [PubMed](https://pubmed.ncbi.nlm.nih.gov/about/) containing search results for the term [Sjögren's Syndrome](https://pubmed.ncbi.nlm.nih.gov/?term=sjogren+syndrome). This dataset is comprised of a single file `pubmed_result_sjogren.xml` which contains info on:

- Article Title
- Article Text
- Journal in which the article was published
- List of Authors with their respective Affiliations (Institutions)
- Keywords

2. The [GRID](https://www.grid.ac/) datasets providing information about public research institutions. This dataset is comprised of 4 different csv files all linked with their grid_id:

- Institutions names `institutes.csv` with fields

  - grid_id
  - name
  - wikipedia_url
  - email_address
  - established (year)

- Addresses of institutions `addresses.csv` with fields

  - grid_id
  - line_1, line_2, line_3
  - lat,lng
  - postcode ,primary ,city ,state ,state_code,country,country_code,geonames_city_id

- Name Aliases of institutions `aliases.csv` with fields

  - grid_id
  - alias

- Relationships between institutions relationships.csv
  - grid_id
  - relationship_type
  - related_grid_id

### Outputs

As you'll learn in these challenges, XML is a deeply nested file format. The main goal of this project is to navigate the PubMed XML file, extracting only relevant fields (see below), enriching and cleaning them using regular expressions and other tools, and finally performing data matching in the affiliations, returning a single csv file.

A specific article can have many authors, and each of these authors can belong to multiple institutions. In order to present this type of nested structure in a flat csv file you will need to 'un-nest' or 'flatten' the data to obtain a single row per affiliation.

![Flattened author-affiliation structure](/relative/images/author_affiliation_flattened_structure.png?raw=true 'Flattened author-affiliation structure')

Once in this format you'll need to clean and enrich it (details in challenges 2-4). The resulting csv should contain the following columns:

- Article PMID
- Article title
- Article keywords
- Article MESH identifiers
- Article year
- Author first name
- Author last name
- Author initials
- Author full name
- Author email
- Affiliation name (as it appears in the PubMed dataset)
- Affiliation name (as it appears in the GRID dataset)
- Affiliation zipcode
- Affiliation country
- Affiliation GRID identifier

## 🛠️ Setup


### Environment variables




## Data Observations

The `pubmed_data` XML structure adheres to the PubMed Central DTD (Document Type Definition) for PubMed articles.

The dataset is structured as a set of articles wrapped within a tag.
As the top level (root) tag `<PubmedArticleSet>` encloses a set of `<PubmedArticle>` tags, each describing an individual article.

Each individual `<PubmedArticle>` contains a `<MedlineCitation>` tag and a `<PubmedData>` tag.

- `<PubmedData>`: Includes the time of publishing and identification details for an article.
- `<MedlineCitation>`: Includes details about the article such as PMID, DateRevised, Article, MedlineJournalInfo, CitationSubset and sometimes a KeywordList and/or a MeshHeadingList.

Details for a specific `Author` can be accessed as such:

- What type of data is stored along with each `Author`?
- How would you find for an `Author` the institutions he's affiliated with?

## Handling the data

The data is parsed in python using python's built-in `xml` library (in particular the `xml.etree.ElementTree` API).

## assumptions

- When extracting country names it's assumed that country names found in affiliations typically adopt a naming similar to those specified in the Python GeonamesCache library.

  - https://pypi.org/project/geonamescache/

- When using nlp to identify matches for institution names from a list of entities, I used a break
  to stop searching through the entities once the similarity threshold had been met.
  - an example list of entities would be `{'Department of Rheumatology', 'Amsterdam Rheumatology & Immunology Center'}`
    This reduced total runtime by approximately 20-25% when using the Jaro-Winkler similarity algorithm.
    However it also assumes that another entity of greater similarity with the true institute name does not occur
    later in the list. I think this is a fair assumption to make:
  - If there are multiple matches meeting the similarity threshold within a single list of entities,
    it is more probable they match with the same true institute regardless of the entity chosen (given the use of a suitably high similarity threshold).
  - At similarity threshold `0.85`, this method produced no erroneous.

# levenshtein worked best + explain why chosen

# list all the files to download and gitignore the rest


# Running the project


