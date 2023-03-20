from flask import Flask, jsonify, render_template, request
import os

import openai
#from dotenv import load_dotenv

app = Flask(__name__)

# load values from the .env file if it exists
#load_dotenv()
OPENAI_API_KEY="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"
openai.api_key = OPENAI_API_KEY
INSTRUCTIONS = """You are an AI assistant that is an expert in personal financial planning.
You know about savings, spending, and investing.
You know how to take advantage of retirement accounts such as IRA, rollover, and Roth IRA.
You understand tax planning as well as estate planning.  You help clients to plan for a comfortable and secured retirement and have strategies to deal with unforeseen events. You also understand insurance products as part of retirement planning.
If you are unable to provide an answer to a question, please respond with the phrase, "I'm not able to help you. Please consult your financial advisor." 
Do not use any external URLs in your answers.  Do not refer to any blogs in our answers.
Format any lists on individual lines with a dash or a space in front of each item."""

#ANSWER_SEQUENCE = "\nAI:"
#QUESTION_SEQUENCE = "\nHuman:"
TEMPERATURE = 0.5
MAX_TOKENS = 500
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6
# limits how many questions we include in the prompt
MAX_CONTEXT_QUESTIONS = 10


def get_response(instructions, previous_questions_and_answers, new_question):
    """Get a response from ChatCompletion

    Args:
        instructions: The instructions for the chat bot - this determines how it will behave
        previous_questions_and_answers: Chat history
        new_question: The new question to ask the bot

    Returns:
        The response text
    """
    # build the messages
    messages = [
        { "role": "system", "content": instructions },
    ]
    # add the previous questions and answers
    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({ "role": "user", "content": question })
        messages.append({ "role": "assistant", "content": answer })
    # add the new question
    messages.append({ "role": "user", "content": new_question })

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=1,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
    )
    return completion.choices[0].message.content


def get_moderation(question):
    """
    Check the question is safe to ask the model

    Parameters:
        question (str): The question to check

    Returns a list of errors if the question is not safe, otherwise returns None
    """

    errors = {
        "hate": "Content that expresses, incites, or promotes hate based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
        "hate/threatening": "Hateful content that also includes violence or serious harm towards the targeted group.",
        "self-harm": "Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
        "sexual": "Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness).",
        "sexual/minors": "Sexual content that includes an individual who is under 18 years old.",
        "violence": "Content that promotes or glorifies violence or celebrates the suffering or humiliation of others.",
        "violence/graphic": "Violent content that depicts death, violence, or serious physical injury in extreme graphic detail.",
    }
    response = openai.Moderation.create(input=question)
    if response.results[0].flagged:
        # get the categories that are flagged and generate a message
        result = [
            error
            for category, error in errors.items()
            if response.results[0].categories[category]
        ]
        return result
    return None

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == "POST":
        previous_questions_and_answers = []
        while True:
            # ask the user for their question
            new_question = request.form['question']
            print(new_question)
            # check the question is safe
            errors = get_moderation(new_question)
            if errors:
                print("Sorry, you're question didn't pass the moderation check:")
                for error in errors:
                    print(error)
                continue
            response = get_response(INSTRUCTIONS, previous_questions_and_answers, new_question)
            print(response)
            # add the new question and answer to the list of previous questions and answers
            previous_questions_and_answers.append((new_question, response))
            output = response
            print(output)
            return jsonify({'new_question': new_question, 'output' : output})
            
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    
    
    
    
    
    