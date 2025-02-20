from llm_insights.prompt import construct_articles, construct_prompt


def test_construct_articles():
    article_extracts = [
        {
            "article_number": "1",
            "article_title": "Title 1",
            "description": "Description 1",
        },
        {
            "article_number": "2",
            "article_title": "Title 2",
            "description": "Description 2",
        },
    ]
    result = construct_articles(article_extracts)
    assert "1" in result
    assert "Title 1" in result
    assert "Description 1" in result
    assert "2" in result
    assert "Title 2" in result
    assert "Description 2" in result


def test_construct_prompt():
    property_name = "Fairness"
    metric_name = "Bias"
    metric_value = "0.2"
    article_extracts = [
        {
            "article_number": "1",
            "article_title": "Title 1",
            "description": "Description 1",
        }
    ]
    result = construct_prompt(
        property_name, metric_name, metric_value, article_extracts
    )
    assert "Fairness" in result
    assert "Bias" in result
    assert "0.2" in result
    assert "1" in result
    assert "Title 1" in result
    assert "Description 1" in result
