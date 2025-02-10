from pydantic import BaseModel


# Sub Agent Schema
class SubAgent(BaseModel):
    """
    Useful when to answer question based on feedback and Instructions.
    It can help with SentimentAnalysis, TopicCategorization, KeywordContextualization, Summarization
    """

# Sentiment Analysis Tool
class SentimentAnalysisTool(BaseModel):
    """
    Useful when to analyze the sentiment of the text.
    """
    query: str

# Topic Categorization Tool
class TopicCategorizationTool(BaseModel):
    """
    Useful when to categorize the text into a specific topic.
    """
    query: str

# Keyword Contextualization Tool
class KeywordContextualizationTool(BaseModel):
    """
    Useful when to contextualize the text based on a specific keyword.
    """
    query: str

# Summarization Tool
class SummarizationTool(BaseModel):
    """
    Useful when to summarize the text.
    """
    query: str
