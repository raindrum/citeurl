"tests for individual citation templates. not all of them are ready yet"

from citeurl import Citator
#from requests import get
#from time import sleep

TESTS = {
    "United States Code": {
        "cite": "42 U.S.C. § 1983",
        "URL": "https://www.law.cornell.edu/uscode/text/42/1983",
        "shortform": "§ 1988(b)",
        "shortform_URL": "https://www.law.cornell.edu/uscode/text/42/1988#b"
    },
    "United States Constitution": {
        "cite": "U.S. Constitution Art. III § 2, cl. 1",
        "URL": "https://constitution.congress.gov/browse/article-3#III_S2_C1",
        "shortform": "Id. at cl. 2",
        "shortform_URL": "https://constitution.congress.gov/browse/article-3#III_S2_C2"
    },
    "U.S. Public Laws": {
        "cite": "Pub. L. 116-344",
        "URL": "https://uscode.house.gov/statutes/pl/116/344.pdf",
        "shortform": None,
        "shortform_URL": None
    },
    "U.S. Statutes at Large": {
        "cite": "120 Stat. 3754",
        "URL": "https://www.govinfo.gov/content/pkg/STATUTE-120/pdf/STATUTE-120-Pg3754.pdf",
        "shortform": None,
        "shortform_URL": None
    },
    "Federal Register": {
        "cite": "85 FR 55292",
        "URL": "https://www.federalregister.gov/documents/search?conditions[term]=85+FR+55292",
        "shortform": None,
        "shortform_URL": None
    },
    "Code of Federal Regulations": {
        "cite": "40 CFR § 70.11(a)",
        "URL": "https://ecfr.federalregister.gov/cfr-reference?cfr%5Bdate%5D=current&cfr%5Breference%5D=40 CFR 70.11#p-70.11(a)",
        "shortform": "Id. at (b)",
        "shortform_URL": "https://ecfr.federalregister.gov/cfr-reference?cfr%5Bdate%5D=current&cfr%5Breference%5D=40 CFR 70.11#p-70.11(b)"
    },
    "Federal Rules of Civil Procedure": {
        "cite": "Fed. R. Civ. P. 12(b)(6)",
        "URL": "https://www.law.cornell.edu/rules/frcp/rule_12#rule_12_b_6",
        "shortform": "Rule 11",
        "shortform_URL": "https://www.law.cornell.edu/rules/frcp/rule_11"
    },
    "Federal Rules of Appellate Procedure": {
        "cite": "Fed. R. App. Proc. 6",
        "URL": "https://www.law.cornell.edu/rules/frap/rule_6",
        "shortform": "Id. at (b)(1)",
        "shortform_URL": "https://www.law.cornell.edu/rules/frap/rule_6#rule_6_b_1"
    },
    "Federal Rules of Criminal Procedure": {
        "cite": "FRCrP Rule 6",
        "URL": "https://www.law.cornell.edu/rules/frcrmp/rule_6",
        "shortform": "Rule 7(c)",
        "shortform_URL": "https://www.law.cornell.edu/rules/frcrmp/rule_7#rule_7_c"
    },
    "Federal Rules of Evidence": {
        "cite": "Fed. R. Evid. 403",
        "URL": "https://www.law.cornell.edu/rules/fre/rule_403",
        "shortform": "Rule 404(b)",
        "shortform_URL": "https://www.law.cornell.edu/rules/fre/rule_404#rule_404_(b)"
    },
    "Immigration and Nationality Act": {
        "cite": "INA § 101(11)",
        "URL": "https://www.law.cornell.edu/uscode/text/8/1101#11",
        "shortform": "§ 237(c)",
        "shortform_URL": "https://www.law.cornell.edu/uscode/text/8/1227#c"
    },
    "Internal Revenue Code": {
        "cite": "IRC § 671",
        "URL": "https://www.law.cornell.edu/uscode/text/26/671",
        "shortform": "§ 673",
        "shortform_URL": "https://www.law.cornell.edu/uscode/text/26/673"
    },
    "Treasury Regulations": {
        "cite": "Treas. Reg. 1.42-1T",
        "URL": "https://ecfr.federalregister.gov/cfr-reference?cfr%5Bdate%5D=current&cfr%5Breference%5D=26 CFR 1.42-1T",
        "shortform": "Id. at (b)",
        "shortform_URL": "https://ecfr.federalregister.gov/cfr-reference?cfr%5Bdate%5D=current&cfr%5Breference%5D=26 CFR 1.42-1T#p-1.42-1T(b)"
    },
    "National Labor Relations Act": {
        "cite": "NLRA § 8(b)(4)",
        "URL": "https://www.law.cornell.edu/uscode/text/29/158#b_4",
        "shortform": "§ 7",
        "shortform_URL": "https://www.law.cornell.edu/uscode/text/29/157"
    },
    "National Labor Relations Board Decisions": {
        "cite": "202 NLRB 538",
        "URL": "https://www.nlrb.gov/cases-decisions/decisions/board-decisions?search_term=&volume=202&page_number=538",
        "shortform": None,
        "shortform_URL": None
    },
    "National Labor Relations Board Slip Opinions": {
        "cite": "365 NLRB No. 156",
        "URL": "https://www.nlrb.gov/cases-decisions/decisions/board-decisions?search_term=&volume=365&slip_opinion_number=156",
        "shortform": None,
        "shortform_URL": None
    },
    "Endangered Species Act": {
        "cite": "ESA § 10",
        "URL": "https://www.law.cornell.edu/uscode/text/16/1539",
        "shortform": "§ 10(b)(2)",
        "shortform_URL": "https://www.law.cornell.edu/uscode/text/16/1539#b_2"
    },
    "Clean Air Act": {
        "cite": "CAA § 171(2)",
        "URL": "https://www.law.cornell.edu/uscode/text/42/7501#2",
        "shortform": "Id. at (3)(A)",
        "shortform_URL": "https://www.law.cornell.edu/uscode/text/42/7501#3_A"
    },
    "Clean Water Act": {
        "cite": "CWA § 404(a)",
        "URL": "https://www.law.cornell.edu/uscode/text/33/1344#a",
        "shortform": "Id. at (b)",
        "shortform_URL": "https://www.law.cornell.edu/uscode/text/33/1344#b"
    },
    "Fair Housing Act": {
        "cite": "FHA § 801",
        "URL": "https://www.law.cornell.edu/uscode/text/42/3601",
        "shortform": "§ 817a",
        "shortform_URL": "https://www.law.cornell.edu/uscode/text/42/3616a"
    },
    "Americans With Disabilities Act": {
        "cite": "ADA § 514",
        "URL": "https://www.law.cornell.edu/uscode/text/42/12213",
        "shortform": "§ 509",
        "shortform_URL": "https://www.law.cornell.edu/uscode/text/42/12209"
    },
    "Uniform Commercial Code": {
        "cite": "UCC 2-104",
        "URL": "https://www.law.cornell.edu/ucc/2/2-104",
        "shortform": None,
        "shortform_URL": None
    },
    "Code of Alabama, 1975": {
        "cite": "Ala. Code § 38-2-6",
        "URL": "http://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/38-2-6.htm",
        "shortform": "§ 26-14-8",
        "shortform_URL": "http://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/26-14-8.htm"
    },
    "Alabama Constitution": {
        "cite": "Ala. Const. Art. VIII, Sec. 177",
        "URL": "https://ballotpedia.org/Article_VIII,_Alabama_Constitution#Section_177",
        "shortform": "Id. at § 178",
        "shortform_URL": "https://ballotpedia.org/Article_VIII,_Alabama_Constitution#Section_178"
    },
    "Alaska Statutes": {
        "cite": "Alaska Stat. § 01.05.011",
        "URL": "http://www.akleg.gov/basis/statutes.asp#01.05.011",
        "shortform": "01.05.016",
        "shortform_URL": "http://www.akleg.gov/basis/statutes.asp#01.05.016"
    },
    "Alaska Constitution": {
        "cite": "Alaska Const. Art. I § 1",
        "URL": "https://ballotpedia.org/Article_I,_Alaska_Constitution#Section_1",
        "shortform": "§ 3",
        "shortform_URL": "https://ballotpedia.org/Article_I,_Alaska_Constitution#Section_3"
    },
    "American Samoa Code": {
        "cite": "Am. Samoa Code § 2.1002",
        "URL": "https://new.asbar.org/code-annotated/2-1002",
        "shortform": "§ 1009(b)",
        "shortform_URL": "https://new.asbar.org/code-annotated/2-1009"
    },
    "American Samoa Constitution": {
        "cite": "Am. Samoa Const. Art. II § 2",
        "URL": "https://ballotpedia.org/Article_II,_American_Samoa_Constitution#Section_2",
        "shortform": "§ 3",
        "shortform_URL": "https://ballotpedia.org/Article_II,_American_Samoa_Constitution#Section_3"
    },
    "Arkansas Code": {
        "cite": "Ark. Code Ann. § 11-6-104",
        "URL": None,
        "shortform": "§ 11-6-107",
        "shortform_URL": None
    },
    "Arkansas Constitution": {
        "cite": "Arkansas Constitution Article 18",
        "URL": "https://ballotpedia.org/Article_18,_Arkansas_Constitution",
        "shortform": "Article 15, § 2",
        "shortform_URL": "https://ballotpedia.org/Article_15,_Arkansas_Constitution#Section_2"
    },
    "Arizona Revised Statutes": {
        "cite": "Ariz. Rev. Stat. § 18-104",
        "URL": "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/18/00104.htm",
        "shortform": "§ 18-105",
        "shortform_URL": "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/18/00105.htm"
    },
    "Arizona Constitution": {
        "cite": "Arizona Constitution Article XII, section 3",
        "URL": "https://ballotpedia.org/Article_12,_Arizona_Constitution#Section_3",
        "shortform": "§ 2",
        "shortform_URL": "https://ballotpedia.org/Article_12,_Arizona_Constitution#Section_2"
    },
    "California Codes": {
        "cite": "California Public Resources Code § 21001.1",
        "URL": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PRC&sectionNum=21001.1",
        "shortform": "§ 21004",
        "shortform_URL": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PRC&sectionNum=21004"
    },
    "California Constitution": {
        "cite": "Cal. Const. Art. XI § 1",
        "URL": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CONS&article=XI&sectionNum=SEC. 1.",
        "shortform": "§ 2",
        "shortform_URL": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CONS&article=XI&sectionNum=SEC. 2."
    },
    "Colorado Revised Statutes": {
        "cite": "Colo. Rev. Stat. § 8-2-113",
        "URL": "https://leg.colorado.gov/sites/default/files/images/olls/crs2020-title-08.pdf#search=8-2-113.",
        "shortform": "§ 8-2-112",
        "shortform_URL": "https://leg.colorado.gov/sites/default/files/images/olls/crs2020-title-08.pdf#search=8-2-112."
    },
    "Colorado Constitution": {
        "cite": "Colo. Const. Art. XIX, Sec. 2",
        "URL": "https://ballotpedia.org/Article_XIX,_Colorado_Constitution#Section_2",
        "shortform": "§ 3",
        "shortform_URL": "https://ballotpedia.org/Article_XIX,_Colorado_Constitution#Section_3"
    },
    "General Statutes of Connecticut": {
        "cite": "Conn. Gen. Stat. § 46b-137",
        "URL": "https://www.lawserver.com/law/state/connecticut/ct-laws/connecticut_statutes_46b",
        "shortform": "§ 121q",
        "shortform_URL": "https://www.lawserver.com/law/state/connecticut/ct-laws/connecticut_statutes_121q"
    },
    "Connecticut Constitution": {
        "cite": "Conn. Const. Art. XIII, Sec. 2",
        "URL": "https://ballotpedia.org/Article_XIII,_Connecticut_Constitution#Section_2",
        "shortform": "Art. VII",
        "shortform_URL": "https://ballotpedia.org/Article_VII,_Connecticut_Constitution"
    },
    "Delaware Code": {
        "cite": "9 Del. C. § 2402(b)",
        "URL": "https://www.lawserver.com/law/state/delaware/de-code/delaware_code_title_9_2402",
        "shortform": "§ 2403",
        "shortform_URL": "https://www.lawserver.com/law/state/delaware/de-code/delaware_code_title_9_2403"
    },
    "Delaware General Corporations Law": {
        "cite": "DGCL § 203",
        "URL": "https://delcode.delaware.gov/title8/c001/sc06/index.shtml#203.",
        "shortform": "§ 244",
        "shortform_URL": "https://delcode.delaware.gov/title8/c001/sc08/index.shtml#244."
    },
    "Delaware Constitution": {
        "cite": "Del. Const. Art. XVI",
        "URL": "https://ballotpedia.org/Article_XVI,_Delaware_Constitution",
        "shortform": "Id. at § 2",
        "shortform_URL": "https://ballotpedia.org/Article_XVI,_Delaware_Constitution#Section_2"
    },
    "District of Columbia Official Code": {
        "cite": "D.C. Code § 40-101",
        "URL": "https://code.dccouncil.us/dc/council/code/sections/40-101.html",
        "shortform": "§ 40-103",
        "shortform_URL": "https://code.dccouncil.us/dc/council/code/sections/40-103.html"
    },
    "Florida Statutes": {
        "cite": "Fla. Stat. § 285.16",
        "URL": "https://www.flsenate.gov/Laws/Statutes/2020/0285.16",
        "shortform": "§ 285.20",
        "shortform_URL": "https://www.flsenate.gov/Laws/Statutes/2020/0285.20"
    },
    "Florida Constitution": {
        "cite": "Florida Constitution Article X, Section 2",
        "URL": "https://www.flsenate.gov/Laws/Constitution#A10S02",
        "shortform": "Section 6",
        "shortform_URL": "https://www.flsenate.gov/Laws/Constitution#A10S06"
    },
    "Georgia Code": {
        "cite": "Ga. Code Ann. § 21-2-417",
        "URL": None,
        "shortform": "§ 38-3-4",
        "shortform_URL": None
    },
    "Georgia Constitution": {
        "cite": "Ga. Const. Art. II, § 1",
        "URL": "https://ballotpedia.org/Article_II,_Georgia_Constitution",
        "shortform": "Id. at para. 2",
        "shortform_URL": "https://ballotpedia.org/Article_II,_Georgia_Constitution"
    },
    "Guam Code": {
        "cite": "11 Guam Code § 72107",
        "URL": None,
        "shortform": "§ 72106",
        "shortform_URL": None
    },
    "Hawaii Revised Statutes": {
        "cite": "Haw. Rev. Stat. § 237-13",
        "URL": "https://www.lawserver.com/law/state/hawaii/hi-statutes/hawaii_statutes_237-13",
        "shortform": "§ 521-8",
        "shortform_URL": "https://www.lawserver.com/law/state/hawaii/hi-statutes/hawaii_statutes_521-8"
    },
    "Hawaii Constitution": {
        "cite": "Hawaii Constitution Article VIII, Section 2",
        "URL": "https://ballotpedia.org/Article_VIII,_Hawaii_Constitution#Section_2",
        "shortform": "§ 6",
        "shortform_URL": "https://ballotpedia.org/Article_VIII,_Hawaii_Constitution#Section_6"
    },
    "Idaho Code": {
        "cite": "Idaho Code § 66-326",
        "URL": "https://legislature.idaho.gov/statutesrules/idstat/Title66/T66CH3/SECT66-326/",
        "shortform": "Id. at (2)",
        "shortform_URL": "https://legislature.idaho.gov/statutesrules/idstat/Title66/T66CH3/SECT66-326/"
    },
    "Idaho Constitution": {
        "cite": "Idaho Const. Art. 2, § 3",
        "URL": "https://ballotpedia.org/Article_II,_Idaho_Constitution#Section_3",
        "shortform": "Art. 1, § 1",
        "shortform_URL": "https://ballotpedia.org/Article_I,_Idaho_Constitution#Section_1"
    },
    "Illinois Compiled Statutes": {
        "cite": "410 ILCS 54/1",
        "URL": "https://www.ilga.gov/legislation/ilcs/fulltext.asp?DocName=041000540K1",
        "shortform": "§ 10",
        "shortform_URL": "https://www.ilga.gov/legislation/ilcs/fulltext.asp?DocName=041000540K10"
    },
    "Illinois Constitution": {
        "cite": "Ill. Const. Art. VII, Sec. 2",
        "URL": "https://ballotpedia.org/Article_VII,_Illinois_Constitution#Section_2",
        "shortform": "§ 3",
        "shortform_URL": "https://ballotpedia.org/Article_VII,_Illinois_Constitution#Section_3"
    },
    "Indiana Code": {
        "cite": "Ind. Code § 9-22-3-2.5",
        "URL": "https://iga.in.gov/legislative/laws/2020/ic/titles/09#09-22-3-2.5",
        "shortform": "§ 9-22-3-3",
        "shortform_URL": "https://iga.in.gov/legislative/laws/2020/ic/titles/09#09-22-3-3"
    },
    "Indiana Constitution": {
        "cite": "Indiana Constitution Article XIII, Section 1",
        "URL": "https://ballotpedia.org/Article_13,_Indiana_Constitution#Section_1",
        "shortform": "Art. 4, § 2",
        "shortform_URL": "https://ballotpedia.org/Article_4,_Indiana_Constitution#Section_2"
    }
}

def test_url_generation():
    """
    make sure each template is properly matching longform and shortform
    citations and generating the expected URLs
    """
    citator = Citator()
    print('Checking each template against sample citations...')
    for template in citator.templates:
        # skip templates that don't have tests yet
        if template.name not in TESTS:
            continue
        
        # try parsing a text where the shortform follows the longform
        test = TESTS[template.name]
        test_string = f"{test['cite']}. {test['shortform'] or ''}"
        found_cites = citator.list_citations(test_string)
        
        print(f'{template.name}: "{test_string}" ... ', end='')
        
        # if there was a shortform, citator should find two citations
        assert len(found_cites) == 2 if test['shortform'] else 1
        
        # make sure the correct template got matched
        assert found_cites[0].template.name == template.name
        
        # check if longform citation has expected URL
        assert found_cites[0].URL == test['URL']
        
        # check if shortform citation (if any) has expected URL
        if len(found_cites) == 2:
            assert found_cites[1].URL == test['shortform_URL']
        
        print('OK')

#def test_urls_validity():
#    "make sure CiteURL's URLs generally don't go to error pages"
#    print('Checking whether test URLs still return valid response codes...')
#    for template in TESTS.values():
#        print(f"{template['cite']} ... ", end='')
#        if not template['URL']:
#            continue
#        response = get(template['URL'])
#        assert response.ok
#        print('OK')
#        sleep(1)
