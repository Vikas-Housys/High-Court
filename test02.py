import re

def get_case_numbers(text):
    """Extracts and formats case numbers from the given text."""

    case_types = {
        "CWP": "CIVIL WRIT PETITION",
        "CRM-M": "CRIMINAL MAIN",
        "CR": "CIVIL REVISION",
        "RSA": "REGULAR SECOND APPEAL",
        "CRR": "CRIMINAL REVISION",
        "CRA-S": "CRIMINAL APPEAL SB",
        "FAO": "FIRST APPEAL ORDER",
        "CM": "CIVIL MISC",
        "CRM": "CRIMINAL MISCELLANEOUS PETITION",
        "ARB": "ARBITRATION ACT CASE (WEF 15/10/03)",
        "ARB-DC": "ARBITRATION CASE (DOMESTIC COMMERCIAL)",
        "ARB-ICA": "ARBITRATION CASE (INTERNATIONAL COMM ARBITRATION)",
        "CA": "CIVIL APPEAL/COMPANY APPLICATION",
        "CA-CWP": "COMMERCIAL APPEAL (WRIT)",
        "CA-MISC": "COMMERCIAL APPEAL (MISC)",
        "CACP": "CONTEMPT APPEALS",
        "CAPP": "COMPANY APPEAL",
        "CCEC": "CUSTOM CENTRAL EXCISE CASE",
        "CCES": "CCES",
        "CEA": "CENTRAL EXCISE APPEAL (WEF 10-11-2003)",
        "CEC": "CENTRAL EXCISE CASE",
        "CEGC": "CENTRAL EXCISE GOLD CASE",
        "CESR": "CENTRAL EXCISE AND SALT REFERENCE",
        "CLAIM": "CLAIMS",
        "CM-INCOMP": "Misc Appl. in Incomplete Case",
        "CMA": "COMPANY MISC. APPLICATION",
        "CMM": "HMA CASES U/S 24",
        "CO": "CIVIL ORIGINAL",
        "CO-COM": "CIVIL ORIGINAL (COMMERCIAL)",
        "COA": "COMPANY APPLICATION",
        "COCP-": "CIVIL ORIGINAL CONTEMPT PETITION",
        "COMM-PET-M": "COMMERCIAL PETITION MAIN",
        "CP": "COMPANY PETITIONS",
        "CP-MISC": "COMMERCIAL PETITION (MISC)",
        "CR-COM": "CIVIL REVISION (COMMERCIAL)",
        "CRA": "CRIMINAL APPEAL",
        "CRA-AD": "CRIMINAL APPEAL ACQUITTAL DB",
        "CRA-AS": "CRIMINAL APPEAL ACQUITTAL SB",
        "CRA-D": "CRIMINAL APPEAL DB",
        "CRACP": "CRIMINAL APPEAL CONTEMPT PETITION",
        "CREF": "CIVIL REFERENCE",
        "CRM-A": "AGAINST ACQUITTALS",
        "CRM-CLT-OJ": "CRIMINAL COMPLAINT (ORIGINAL SIDE)",
        "CRM-W": "CRM IN CRWP",
        "CROCP": "CRIMINAL ORIGINAL CONTEMPT PETITION",
        "CRR(F)": "CRIMINAL REVISION (FAMILY COURT)",
        "CRREF": "CRIMINAL REFERENCE",
        "CRWP": "CRIMINAL WRIT PETITION",
        "CS": "CIVIL SUIT",
        "CS-OS": "CIVIL SUIT-ORIGINAL SIDE",
        "CUSAP": "CUSTOM APPEAL (WEF 17/7/2004)",
        "CWP-COM": "CIVIL WRIT PETITION (COMMERCIAL)",
        "CWP-PIL": "CIVIL WRIT PETITION PUBLIC INTEREST LITIGATION",
        "DP": "DIVORCE PETITION",
        "EA": "EXECUTION APPL",
        "EDC": "ESTATE DUTY CASE",
        "EDREF": "ESTATE DUTY REFERENCE",
        "EFA": "EXECUTION FIRST APPEAL",
        "EFA-COM": "EXECUTION FIRST APPEAL (COMMERCIAL)",
        "EP": "ELECTION PETITIONS",
        "EP-COM": "EXECUTION PETITION (COMMERCIAL)",
        "ESA": "EXECUTION SECOND APPEAL",
        "FAO(FC)": "FAO (FAMILY COURT)",
        "FAO-C": "FAO (CUS AND MTC)",
        "FAO-CARB": "FIRST APPEAL FROM ORDER (COMMERCIAL ARBITRATION)",
        "FAO-COM": "FIRST APPEAL FROM ORDER (COMMERCIAL)",
        "FAO-ICA": "FIRST APPEAL FROM ORDER (INTERNATIONAL COMM ARBI.)",
        "FAO-M": "FIRST APPEAL ORDER-MATRIMONIAL",
        "FEMA-APPL": "FEMA APPEAL",
        "FORM-8A": "FORM-8A",
        "GCR": "GOLD CONTROL REFERENCE",
        "GSTA": "GOODS AND SERVICES TAX APPEAL",
        "GSTR": "GENERAL SALES TAX REFERENCE",
        "GTA": "GIFT TAX APPEAL",
        "GTC": "GIFT TAX CASE",
        "GTR": "GIFT TAX REFERENCE",
        "GVATR": "GENERAL VAT REFERENCES",
        "INCOMP": "INCOMPLETE OBJECTION CASE",
        "INTTA": "INTEREST TAX APPEAL",
        "IOIN": "INTERIM ORDER IN",
        "ITA": "INCOME TAX APPEAL",
        "ITC": "INCOME TAX CASES",
        "ITR": "INCOME TAX REFERENCE",
        "LPA": "LATTER PATENT APPEALS",
        "LR": "LIQUIDATOR REPORT",
        "MATRF": "MATROMONIAL REFERENCE",
        "MRC": "MURDER REFERENCE CASE",
        "O&M": "ORIGINAL & MISCELLANEOUS",
        "OLR": "OFFICIAL LIQUIDATOR REPORT",
        "PBPT-APPL": "PROHIBITION OF BENAMI PROPERTY TRANSACTION APPEAL",
        "PBT": "PROBATE",
        "PMLA-APPL": "PREVENTION OF MONEY LAUNDERING APPEAL",
        "PVR": "PB VAT REVISION",
        "RA": "REVIEW APPL",
        "RA-CA": "REVIEW IN COMPANY APPEAL",
        "RA-CP": "REVIEW IN COMPANY PETITION",
        "RA-CR": "REVIEW IN CR",
        "RA-CW": "REVIEW IN CWP",
        "RA-LP": "REVIEW IN LPA",
        "RA-RF": "REVIEW APPLICATION IN RFA",
        "RA-RS": "REVIEW IN RSA",
        "RCRWP": "REVIEW IN CRCWP",
        "RERA-APPL": "RERA APPEAL",
        "RFA": "REGULAR FIRST APPEAL",
        "RFA-COM": "REGULAR FIRST APPEAL (COMMERCIAL)",
        "RP": "RECRIMINATION PETITION",
        "SA": "SERVICE APPEAL",
        "SAO": "SECOND APPEAL ORDER",
        "SAO(FS)": "SAO FOOD SAFETY",
        "SDR": "STATE DUTY REFERENCE",
        "STA": "SALES TAX APPEAL",
        "STC": "SALES TAX CASES",
        "STR": "SALE TAX REFERENCE",
        "TA": "TRANSFER APPLICATION",
        "TA-COM": "TRANSFER APPLICATION (COMMERCIAL)",
        "TC": "TAKENUP CASES",
        "TCRIM": "TRANSFER CRIMINAL PETITION",
        "TEST": "TEST",
        "UVA": "UT VAT APPEAL",
        "UVR": "UT VAT REVISION",
        "VATAP": "VAT APPEAL",
        "VATCASE": "VALUE ADDED TAX CASE",
        "VATREF": "VAT REFERENCE",
        "WTA": "WEALTH TAX APPEAL",
        "WTC": "WEALTH TAX CASES",
        "WTR": "WEALTH TAX REFERENCE",
        "XOBJ": "CROSS OBJECTION",
        "XOBJC": "CROSS OBJECTION IN CR",
        "XOBJL": "CROSS OBJECTION IN LPA",
        "XOBJR": "CROSS OBJECTION IN RFA",
        "XOBJS": "CROSS OBJECTION IN RSA",
    }

    # Regex for properly formatted case numbers
    pattern_hyphenated = r'\b[A-Z]+(?:-[A-Z]+)*-\d+(?:-[A-Z]+)*-(?:1[6-9]\d{2}|20\d{2}|21\d{2}|2200)\b'

    # Regex for improperly formatted case numbers with spaces
    pattern_unformatted = r'\b([A-Z]+)\s?(\d{3,6})\s?([A-Z]*)\s?(1[6-9]\d{2}|20\d{2}|21\d{2}|2200)\b'
    
    # Regex for case numbers written as a single block without spaces or hyphens
    pattern_blocked = r'\b([A-Z]+)(\d{3,6})([A-Z]*)(1[6-9]\d{2}|20\d{2}|21\d{2}|2200)\b'
    
    # Extract correctly formatted case numbers
    case_numbers = set(re.findall(pattern_hyphenated, text))

    # Extract and format improperly formatted case numbers with spaces
    formatted_cases = { "-".join(filter(None, m)) for m in re.findall(pattern_unformatted, text) }
    
    # Extract and format case numbers written as a single block
    formatted_blocked_cases = { "-".join(filter(None, m)) for m in re.findall(pattern_blocked, text) }
    
    # Combine all extracted case numbers and remove duplicates
    return sorted(case_numbers | formatted_cases | formatted_blocked_cases)


# Test with additional cases
print(get_case_numbers("RSA-1052-2024, RSA-192-2024, RSA-332-2024, PWD1276452021, MR 764532 2020, CRMM306682018, CM1216C2024, CM 155 C 2024, CM 1829 CWP 2023"))
print(get_case_numbers("my case number is PWD 36548 2021"))
print(get_case_numbers("CRAS7392024"))
