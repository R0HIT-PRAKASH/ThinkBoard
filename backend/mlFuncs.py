# ---------------script 1 requirements------------------------
import cohere
import pandas as pd

# ----------------script 2 requirements------------------------
import os
import openai

# Cohere Credentials
api_key = 'UZZiknNo4RNoGAIKAFcCzeESZq58IV07oiWoGory'
co = cohere.Client(api_key)

# OpenAI Credentials
openai.organization = "org-odenvdznd4FpkAvZVt1nS3pJ"
#openai.api_key = os.getenv("")
openai.api_key = "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"


def get_predictions(summary):
    prompt = "Give me a list of the top 5 relevant topics related to " + summary

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.6,
        top_p=1,
        max_tokens=64,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text


def get_summary(input_api):
    prompt = '''"I want to make a dynamic schedule builder that automatically schedules your tasks and events so that it works with your personal priorities and interests, and it will learn from my patterns as a user to suit me better in the long run. I also think it's a good idea to make a tracker app that tracks your expenses, savings, and budget and learns from the user's patterns to help them be more financially savvy and maybe eventually gather smart insights about how they can go about investments. I also want to make a brainstorming assistant app so that whenever I dump large bodies of text containing ideas of projects I want to do for a hackathon, this app will help me organize my thoughts so that I have a final idea I can work on for my hackathon project. Lastly, I want to make an app that locates the closest public washrooms to me based on my GPS and also gives me user ratings so I know whether the bathroom is decent or disgusting."
    Features of your brain dump: "Smart schedule planner, budget tracker assistant, brainstorming assistant, public washroom finder"
    ---
    "For a project idea I want to build from a large language model to generate NLP training datasets for various applications related to NLP modeling. Another project I want to work on is an app that accuractely corrects your accent, enunciation, and phonetics when learning a new language. Also, I want an app that uses reverse large language models so that from a short summary, this app will automatically generate a well-written essay for me."
    Features of your brain dump: "NLP training dataset generator, language accent corrector, automatic essay writer"
    ---
    "{str_input}"
    Features of your brain dump:"'''.format(str_input=input_api)

    n_generations = 5

    prediction = co.generate(
        model='xlarge',
        prompt=prompt,
        return_likelihoods='GENERATION',
        stop_sequences=['"'],
        max_tokens=50,
        temperature=0.8,
        num_generations=n_generations,
        k=0,
        p=0.75)

    gens = []
    likelihoods = []
    for gen in prediction.generations:
        gens.append(gen.text)

        sum_likelihood = 0
        for t in gen.token_likelihoods:
            sum_likelihood += t.likelihood

        likelihoods.append(sum_likelihood)

    pd.options.display.max_colwidth = 200
    df = pd.DataFrame({'generation': gens, 'likelihood': likelihoods})
    df = df.drop_duplicates(subset=['generation'])
    df = df.sort_values('likelihood', ascending=False, ignore_index=True)
    return(df["generation"])
