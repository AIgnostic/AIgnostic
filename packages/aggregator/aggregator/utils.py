from pydantic import BaseModel

LEGISLATION_INFORMATION = {}

class FrontendInfo(BaseModel):
    legislation: list[str]

def get_legislation_information():
    def create_legislation_info(name, url):
        return {
            "name": name,
            "url": url,
            "article_extract": lambda article: f"/{article}-art"
        }

    return {
        "gdpr": create_legislation_info("GDPR", "https://gdpr-info.eu/"),
        "eu_ai": create_legislation_info("EU AI Act", "https://ai-act-law.eu/")
    }

# FIX FUNCTION
def update_legislation_information(labels: list[str]):
    global LEGISLATION_INFORMATION
    legislation_information = get_legislation_information()
    filtered_legislation_information = {key: value for key, value in legislation_information.items() if value["name"] in labels}
    LEGISLATION_INFORMATION = filtered_legislation_information

LEGISLATION_INFORMATION = get_legislation_information()