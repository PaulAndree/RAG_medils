
python retrieval_metrics_all.py --questions /home/peyzaguirre/learning/RAG_medils/evaluation/questions_GT_all/nexus_questions_spanish_GT.json --judge-provider openai --model gpt-4.1-mini



For each question in /home/peyzaguirre/learning_1/evaluation/questions_GT/nexus_questions_english_doc_only.json
I want to call the RAG API http://localhost:8004/ method : @app.post("/v1/query") 


{
  "question": question,
  "limit": 5,
  "retrievals": ["passage", "summaries", "graph"]
}

and evaluate the retrieval results of each type of representation (i.e. "passage", "summaries", "graph") against the ground truth which is located in the same json from the question, with the key value "evidence": ["text":]

The retrieval evaluation should be performed using ranx https://amenra.github.io/ranx/run/  — Retrieval evaluation
The metrics we are interested are : Hit · Recall · MRR · MAP · nDCG

So for each type of representation we should get 5 metrics. 
The code should be located at :  /home/peyzaguirre/learning_1/evaluation/retrieval_metrics.py