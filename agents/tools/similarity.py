# agents/tools/similarity.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def is_similar(text1, text2, threshold=0.85):
    """
    Сравнивает два текста и возвращает True, если их сходство выше порога.
    
    :param text1: Первый текст
    :param text2: Второй текст
    :param threshold: Порог сходства (по умолчанию 0.85)
    :return: bool
    """
    if not text1 or not text2:
        return False

    texts = [text1.strip(), text2.strip()]
    vectorizer = TfidfVectorizer().fit(texts)
    tfidf = vectorizer.transform(texts)
    similarity = cosine_similarity(tfidf[0], tfidf[1])[0][0]

    return similarity >= threshold
