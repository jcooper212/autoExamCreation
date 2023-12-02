
import pandas as pd
import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy import text

from dotenv import load_dotenv
import openai
import os
import json


def create_prompt(topic, num_questions, num_ans):
    prompt = f"Create a multiple choice quiz on the topic of {topic} consisting of {num_questions} questions"\
                +f"Each question should have {num_ans} options. " \
                +f"Also include the correct answer for each question using starting string 'Correct Answer:'"
    return prompt

def prompt_input():
    nlp_text = input('Enter the topic for the quiz: ')
    return nlp_text

def handle_response(response):
    query = response['choices'][0]['text']
    #print(response)
    return query

def create_student_view(test, num_questions):
    student_view = {1: ''}
    qstn_num =1
    for line in test.split('\n'):
        if not line.startswith("Correct Answer:"):
            student_view[qstn_num] += line+ '\n'
        else:
            if qstn_num < num_questions:
                qstn_num +=1
                student_view[qstn_num]= ''
    return student_view

def extract_answers(test, num_questions):
        answers = {1: ''}
        ans_num =1
        for line in test.split('\n'):
            if line.startswith("Correct Answer:"):
                answers[ans_num] += line+ '\n'
            else:
                if ans_num < num_questions:
                    ans_num +=1
                    answers[ans_num]= ''
        return answers

def take_test(student_view):
    student_answers = {}
    for question, question_view in student_view.items():
        print(question_view)
        answer = input("Enter your answer: ")
        student_answers[question] = answer
    return student_answers

def grade_exam(correct_ans_dict, student_ans_dict, num_questions):
    correct_ans = 0
    for question, answer in student_ans_dict.items():
        if answer.upper() == correct_ans_dict[question][16]:
            correct_ans +=1
    grade = 100*correct_ans/num_questions
    if grade < 60:
        passed = "NO PASS"
    else:
        passed = "PASS"
    return f"{correct_ans}/{num_questions} correct. You got {grade} grade, {passed}"
######################
##call the openai completion calls

###load ENV VARS
load_dotenv()
openai.api_key = os.getenv("OPEN_AI_KEY")
openai.organization = os.getenv("OPEN_AI_ORG")

NUM_QSTNS=4
subject = prompt_input()
response = openai.Completion.create(
    model = "davinci-002",
    prompt = create_prompt(subject, NUM_QSTNS, NUM_QSTNS),
    temperature = 0.7,
    max_tokens = 256
)
print(handle_response(response))
##parse questions and answers
student_view = create_student_view(handle_response(response), NUM_QSTNS)
answers = extract_answers(handle_response(response), NUM_QSTNS)
