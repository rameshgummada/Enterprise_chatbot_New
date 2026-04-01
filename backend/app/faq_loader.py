import pandas as pd

def load_faq(path="data/faq.csv"):
    df = pd.read_csv(path)
    docs = [{"question": q, "answer": a} for q, a in zip(df["question"], df["answer"])]
    return docs
