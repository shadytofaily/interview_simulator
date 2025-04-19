import yaml
from pathlib import Path
from jinja2 import Template

PROMPTS_DIR = Path(__file__).parent / "prompts"
PERSONAS_DIR = PROMPTS_DIR / "personas"

def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def render_persona_prompt(persona_name: str, skill: str) -> str:
    # Загрузка шаблона
    template_data = load_yaml(PROMPTS_DIR / "persona_system_prompt.yaml")
    template_str = template_data["template"]
    template = Template(template_str)

    # Загрузка YAML профиля персоны
    persona_data = load_yaml(PERSONAS_DIR / f"{persona_name}.yaml")

    # Подставляем значения в шаблон (поддержка дополнительных полей)
    return template.render(
        persona=persona_data.get("persona"),
        behavior=persona_data.get("behavior"),
        experience=persona_data.get("experience"),
        key_skills=persona_data.get("key_skills"),
        achievements=persona_data.get("achievements"),
        skill=skill
    )

def render_star_prompt(message: str, skill: str) -> str:
    path = PROMPTS_DIR / "star_prompt.yaml"
    template_data = load_yaml(path)
    template = Template(template_data["template"])
    return template.render(message=message.strip(), skill=skill)

VALUES_DIR = PROMPTS_DIR / "values"

def render_value_prompt(value_name: str, message: str) -> str:
    """
    Рендерит system prompt для оценки корпоративной ценности.
    """
    path = VALUES_DIR / f"{value_name}.yaml"
    data = load_yaml(path)

    template = Template(
        """Вы HR-специалист и оцениваете ответ кандидата на соответствие корпоративной ценности "{{ value_name }}".

Описание ценности:
{{ description }}

Ответ кандидата:
{{ message }}

Признаки, на которые стоит обратить внимание:
- {{ indicators | join('\n- ') }}

Сделайте краткий вывод: соответствует / не соответствует, и дайте рекомендацию HR.
"""
    )

    return template.render(
        value_name=data["value_name"],
        description=data["description"],
        indicators=data["indicators"],
        message=message.strip()
    )

