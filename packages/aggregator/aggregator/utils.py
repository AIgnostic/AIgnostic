from pydantic import BaseModel
from common.models import LegislationList, LegislationInfo, LegislationInformation 



def create_legislation_info(name, url):
    return LegislationInfo(
        name=name,
        url=url,
        article_extract=lambda article_number: f"art-{article_number}-{name.lower().replace(' ', '_')}"
    )

# LEGISLATION_INFORMATION = {
#     "gdpr": create_legislation_info("GDPR", "https://gdpr-info.eu/"),
#     "eu_ai": create_legislation_info("EU AI Act", "https://ai-act-law.eu/")
# }

LEGISLATION_INFORMATION = {
    "gdpr": LegislationInfo(
        name="GDPR",
        url="https://gdpr-info.eu/",
        article_extract=lambda article_number: f"art-{article_number}-gdpr"
    ), 
    "eu_ai": LegislationInfo(
        name="EU AI Act",
        url="https://ai-act-law.eu/",
        article_extract=lambda article_number: f"article/{article_number}/"
    )
}

# FIX FUNCTION
def update_legislation_information(labels: list[str]):
    legislation_information = get_legislation_information()
    filtered_legislation_information = {key: value for key, value in legislation_information.items() if value["name"] in labels}
    return filtered_legislation_information