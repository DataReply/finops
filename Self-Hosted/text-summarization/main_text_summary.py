import logging
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from langchain_ollama.llms import OllamaLLM
from datasets import load_dataset
#from rouge_score import rouge_scorer
#from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
#from nltk.translate.meteor_score import meteor_score
#import nltk
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Download NLTK data (required for METEOR)
#nltk.download('wordnet')
#nltk.download('omw-1.4')

# Initialize ROUGE scorer
#rouge = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

# ------------------------------
# FUNCTION: Summarize text
# ------------------------------
def summarize_text(text, model_name):
    try:
        llm = OllamaLLM(model=model_name, temperature=0.3)
        prompt = (
            "Summarize the following text in **exactly 50 words or fewer**. "
            "Make sure to include only the most essential details. Do NOT exceed 50 words:\n\n"
            f"{text}\n\n"
            "Your response MUST be at most 50 words."
        )
        summary = llm.invoke(prompt)
        return summary
    except Exception as e:
        logging.error(f"Error summarizing text with {model_name}: {e}")
        return None

# ------------------------------
# FUNCTION: Evaluate summaries
# ------------------------------
'''def evaluate_summary(generated_summary, reference_summary):
    try:
        # ROUGE scores
        rouge_scores = rouge.score(generated_summary, reference_summary)
        # Tokenize reference and generated summaries
        reference_tokens = [reference_summary.split()]
        generated_tokens = generated_summary.split()
         # Apply BLEU smoothing
        smooth_fn = SmoothingFunction().method1  # Smoothing prevents zero scores for low n-gram overlap
        bleu_score = sentence_bleu(reference_tokens, generated_tokens, smoothing_function=smooth_fn)
        # METEOR score
        meteor_score_value = meteor_score(reference_tokens, generated_tokens)
        
        return {
            'rouge1': rouge_scores['rouge1'].fmeasure,
            'rouge2': rouge_scores['rouge2'].fmeasure,
            'rougeL': rouge_scores['rougeL'].fmeasure,
            'bleu': bleu_score,
            'meteor': meteor_score_value
        }
    except Exception as e:
        logging.error(f"Error evaluating summary: {e}")
        return None  '''

# ------------------------------
# MAIN FUNCTION
# ------------------------------
if __name__ == '__main__':
    # Grab Currrent Time Before Running the Code
#    start = time.time()
    # Load dataset
    ds = load_dataset("abisee/cnn_dailymail", "1.0.0")
    
    # Initialize scores
#    llama_scores = {'rouge1': 0, 'rouge2': 0, 'rougeL': 0, 'bleu': 0, 'meteor': 0}
#    mistral_scores = {'rouge1': 0, 'rouge2': 0, 'rougeL': 0, 'bleu': 0, 'meteor': 0}
    iterations = 10  # Number of samples to evaluate
    with ThreadPoolExecutor() as executor:
        futures = []
        for interation in range(0, iterations):
            print("#### Iteration:", interation+1, "####")
            for i in range(9000, 9200):
                try:
    #               iterations += 1
                    logging.info(f"Processing Article: {i}")
                    
                    # Get reference summary
                    reference_summary = ds['train'][i]['highlights']
                    
                    # Generate summaries
                    summary_llama = summarize_text(ds['train'][i]['article'], "llama3")
                    summary_mistral = summarize_text(ds['train'][i]['article'], "mistral")
                    logging.info("Llama Model Summary:\n" + summary_llama)
                    logging.info("Mistral Model Summary:\n" + summary_mistral)
                except Exception as e:
                    logging.error(f"Error processing article {i}: {e}")
#    end = time.time()
#    total_time = end - start
#    print("\nTotal Execution time:"+ str(total_time))
                
'''                if summary_llama and summary_mistral:
                    # Evaluate summaries
                    llama_eval = evaluate_summary(summary_llama, reference_summary)
                    mistral_eval = evaluate_summary(summary_mistral, reference_summary)
                    
                    if llama_eval and mistral_eval:
                        # Accumulate scores
                        for metric in llama_scores.keys():
                            llama_scores[metric] += llama_eval[metric]
                            mistral_scores[metric] += mistral_eval[metric] '''
                    
                    # Print summaries and scores
#                    logging.info(f"\nSample {iterations}")
#                    logging.info("Article: ", ds['train'][i]['article'])              
#                    logging.info("Llama Model Summary:\n" + summary_llama)
#                    logging.info("Llama Evaluation Scores:" + str(llama_eval))
#                    logging.info("Mistral Model Summary:\n" + summary_mistral)
#                    logging.info("Mistral Evaluation Scores:" + str(mistral_eval))
            

    # Average scores
'''    for metric in llama_scores.keys():
        llama_scores[metric] /= iterations
        mistral_scores[metric] /= iterations

    # Print final averaged scores
    logging.info("\n############## Average Scores for " + str(iterations) + " samples ##############")
    logging.info("Llama Scores:" + str(llama_scores))
    logging.info("Mistral Scores:" + str(mistral_scores)) '''