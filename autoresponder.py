"""
Autoresponder logic - classification and response generation
"""
import json
from openai import OpenAI
from prompts import (
    CONTEXT,
    CLASSIFIER_PROMPT,
    STRONG_POSITIVE_PROMPT,
    STRONG_POSITIVE_EXAMPLES,
    SOFT_POSITIVE_PROMPT,
    SOFT_POSITIVE_EXAMPLES,
    NEUTRAL_PROMPT,
    NEUTRAL_EXAMPLES,
    SOFT_OBJECTION_PROMPT,
    SOFT_OBJECTION_EXAMPLES,
    HARD_NO_RESPONSE,
)


class Autoresponder:
    def __init__(self, api_key: str, calendar_link: str = "https://cal.com/your-calendar"):
        self.client = OpenAI(api_key=api_key)
        self.calendar_link = calendar_link
        self.model = "gpt-4o"

    def classify(self, message: str) -> dict:
        """Classify the incoming message into a category"""
        prompt = CLASSIFIER_PROMPT.format(message=message)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        content = response.choices[0].message.content.strip()

        # Parse JSON from response
        try:
            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            return {
                "category": "NEUTRAL",
                "confidence": "low",
                "manual_required": True
            }

    def _build_messages(self, system_prompt: str, examples: list, message: str) -> list:
        """Build messages list with few-shot examples"""
        messages = [{"role": "system", "content": system_prompt}]

        for ex in examples:
            role = ex["role"]
            content = ex["content"].format(calendar_link=self.calendar_link)
            messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": message})
        return messages

    def generate_response(self, message: str, category: str) -> str:
        """Generate a response based on the category"""

        if category == "HARD_NO":
            return HARD_NO_RESPONSE

        if category == "STRONG_POSITIVE":
            system_prompt = STRONG_POSITIVE_PROMPT.format(
                context=CONTEXT,
                calendar_link=self.calendar_link,
                message="{message}"
            )
            examples = STRONG_POSITIVE_EXAMPLES

        elif category == "SOFT_POSITIVE":
            system_prompt = SOFT_POSITIVE_PROMPT.format(
                context=CONTEXT,
                message="{message}"
            )
            examples = SOFT_POSITIVE_EXAMPLES

        elif category == "NEUTRAL":
            system_prompt = NEUTRAL_PROMPT.format(
                context=CONTEXT,
                message="{message}"
            )
            examples = NEUTRAL_EXAMPLES

        elif category == "SOFT_OBJECTION":
            system_prompt = SOFT_OBJECTION_PROMPT.format(
                context=CONTEXT,
                message="{message}"
            )
            examples = SOFT_OBJECTION_EXAMPLES
        else:
            return "I'll get back to you shortly."

        messages = self._build_messages(system_prompt, examples, message)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=150,
        )

        return response.choices[0].message.content.strip()

    def process(self, message: str) -> dict:
        """Full pipeline: classify and generate response"""
        classification = self.classify(message)
        category = classification.get("category", "NEUTRAL")

        response = self.generate_response(message, category)

        return {
            "category": category,
            "confidence": classification.get("confidence", "medium"),
            "manual_required": classification.get("manual_required", False),
            "response": response
        }
