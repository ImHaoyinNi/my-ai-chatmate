import yaml


class Persona:
    def __init__(self, name: str, age: int, prompt: str, voice: str) -> None:
        self.name = name
        self.age = age
        self.prompt = prompt
        self.voice = voice

def civen() -> Persona:
    with open("./civen.yaml", "r") as file:
        data = yaml.safe_load(file)
    prompt = data["prompt"]
    formatted_prompt = prompt.replace("{{ name }}", data['name']).replace("{{ age }}", str(data['age']))
    return Persona(data['name'], data['age'], formatted_prompt, data['voice'])


if __name__ == '__main__':
    civen()
