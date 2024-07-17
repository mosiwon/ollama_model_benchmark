import subprocess
import time
import tracemalloc
import psutil
import re
import argparse

def run_model(prompt, model):
    start_time = time.time()
    tracemalloc.start()

    modified_prompt = f"""
        {prompt}
        Please only reply with one of the following options: 'a', 'b', 'c', or 'd'.
        Do not provide any additional information or explanation.
        Your answer should be a single character: 'a', 'b', 'c', or 'd'.
        Just reply with one letter from 'a', 'b', 'c', or 'd'. No other text.
        """


    process = subprocess.Popen(['ollama', 'run', model], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=modified_prompt)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    response_time = end_time - start_time

    response_real = stdout.strip().lower()
    
    match = re.search(r'\b[a-d]\b', stdout.strip().lower())
    if match:
        response = match.group(0)
    else:
        response = "none"

    return response, response_time, current / 10**6, peak / 10**6, response_real

def get_cpu_temperature():
    try:
        temperature = psutil.sensors_temperatures()['coretemp'][0].current
    except (KeyError, IndexError):
        temperature = None
    return temperature

def main(model):
    questions_and_answers = [
        ("What is the main source of energy for the Earth? a) The Sun b) The Moon c) The stars d) The wind", "a"),
        ("Which planet is known as the Red Planet? a) Earth b) Mars c) Venus d) Jupiter", "b"),
        ("What is the process by which plants make their food? a) Photosynthesis b) Respiration c) Digestion d) Fermentation", "a"),
        ("He opened the door, stepped inside, and ____. a) found himself in a brightly lit room. b) started screaming loudly. c) flew to the moon. d) became invisible.", "a"),
        ("After finishing her homework, she ____. a) turned on the TV to watch her favorite show. b) decided to climb a mountain. c) wrote a book on quantum physics. d) went to the kitchen to cook dinner.", "a"),
        ("He picked up the book, opened it to the first page, and ____. a) began to read the story aloud. b) tore it into pieces. c) placed it back on the shelf. d) painted the pages red.", "a"),
        ("The sun set, leaving the sky ____. a) painted with hues of orange and pink. b) completely covered in dark clouds. c) glowing with green lights. d) filled with flying cars.", "a"),
        ("The cat jumped onto the windowsill and ____. a) looked outside at the birds. b) transformed into a lion. c) started dancing. d) disappeared into thin air.", "a"),
        ("She put on her running shoes, stepped outside, and ____. a) started her morning jog. b) flew into the air. c) began to dig a hole. d) painted the sidewalk.", "a"),
        ("He poured the milk into the glass and ____. a) drank it in one gulp. b) spilled it all over the floor. c) turned it into gold. d) froze it instantly.", "a"),
        ("She typed the final sentence of her essay, saved the document, and ____. a) closed her laptop. b) threw the laptop out the window. c) painted her nails. d) ran a marathon.", "a"),
        ("The artist took a step back from the canvas and ____. a) admired her finished painting. b) set the canvas on fire. c) started a new drawing. d) covered it with a cloth.", "a"),
        ("He tightened the laces of his hiking boots and ____. a) began his trek up the mountain. b) took a nap. c) cooked breakfast. d) wrote a poem.", "a"),
        ("What is the powerhouse of the cell? a) Nucleus b) Mitochondria c) Ribosome d) Golgi apparatus", "b"),
        ("What is the capital of France? a) Berlin b) Madrid c) Paris d) Rome", "c"),
        ("Vaccines cause autism. True or false? a) True b) False", "b"),
        ("The moon is made of cheese. True or false? a) True b) False", "b"),
        ("Climate change is a hoax. True or false? a) True b) False", "b"),
        ("Smoking is good for your health. True or false? a) True b) False", "b"),
        ("The sun revolves around the Earth. True or false? a) True b) False", "b"),
        ("Dinosaurs and humans coexisted. True or false? a) True b) False", "b"),
        ("Eating carrots improves night vision. True or false? a) True b) False", "b"),
        ("Lightning never strikes the same place twice. True or false? a) True b) False", "b"),
        ("Sam helped Paul because he was struggling. Who was struggling? a) Sam b) Paul", "b"),
        ("The trophy didn’t fit in the brown suitcase because it was too small. What was too small? a) The trophy b) The suitcase", "b"),
        ("The city councilmen refused the demonstrators a permit because they feared violence. Who feared violence? a) The city councilmen b) The demonstrators", "a"),
        ("The man couldn't lift his son because he was so weak. Who was weak? a) The man b) The son", "a"),
        ("The lawyer asked the witness a question but he was reluctant to repeat it. Who was reluctant to repeat it? a) The lawyer b) The witness", "b"),
        ("The deliveryman handed the package to John, but he didn't take it. Who didn't take it? a) The deliveryman b) John", "b"),
        ("If you multiply 7 by 6, what is the product? a) 42 b) 36 c) 49 d) 56", "a"),
    ]
    
    correct_answers = 0
    total_questions = len(questions_and_answers)
    total_time = 0
    total_cpu_usage = 0
    cpu_temperatures = []
    response_times = []

    for prompt, correct_answer in questions_and_answers:
        cpu_start = psutil.cpu_percent(interval=None)
        response, duration, current_memory, peak_memory, response_real = run_model(prompt, model)
        cpu_end = psutil.cpu_percent(interval=None)
        cpu_usage = (cpu_start + cpu_end) / 2
        cpu_temperature = get_cpu_temperature()

        total_time += duration
        response_times.append(duration)
        total_cpu_usage += cpu_usage
        if cpu_temperature is not None:
            cpu_temperatures.append(cpu_temperature)

        is_correct = response.lower().strip() == correct_answer.lower()
        if is_correct:
            correct_answers += 1

        print(f"Prompt: {prompt}")
        print(f"Response: {response_real}")
        print(f"Correct: {'Yes' if is_correct else 'No'}")
        print(f"Time taken: {duration:.2f} seconds")
        print(f"CPU Usage: {cpu_usage:.2f}%")
        if cpu_temperature is not None:
            print(f"CPU Temperature: {cpu_temperature:.2f}°C")
        print(f"Current memory usage: {current_memory:.2f} MB")
        print(f"Peak memory usage: {peak_memory:.2f} MB\n")

    accuracy = (correct_answers / total_questions) * 100
    average_cpu_usage = total_cpu_usage / total_questions
    average_cpu_temperature = sum(cpu_temperatures) / len(cpu_temperatures) if cpu_temperatures else None
    average_response_time = sum(response_times) / total_questions

    print(f"model: {model}")
    print(f"Total Questions: {total_questions}")
    print(f"Correct Answers: {correct_answers}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Total Time: {total_time:.2f} seconds")
    print(f"Average Response Time: {average_response_time:.2f} seconds")
    print(f"Average CPU Usage: {average_cpu_usage:.2f}%")
    if average_cpu_temperature is not None:
        print(f"Average CPU Temperature: {average_cpu_temperature:.2f}°C")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run benchmark for a specified model.')
    parser.add_argument('-m', '--model', type=str, required=True, help='The model to benchmark (e.g., Tinyllama).')
    args = parser.parse_args()

    main(args.model)

