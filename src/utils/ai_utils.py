from config.settings.base import AGENT_LLM_MODEL, TEMPERATURE, AGENT_LLM_ENGINE


def is_ai_engine_supported_func(target):
    result = AGENT_LLM_ENGINE
    if target == "llama_index":
        return target
    elif target == "langchain_sql_chain":
        return target
    elif target == "langchain_agent":
        return target
    elif not target or target == "default":
        return target

    return result

def is_ai_model_supported_func(target):
    result = AGENT_LLM_MODEL
    if target == "gpt-3.5":
        return "gpt-3.5-turbo-1106"
    elif target == "gpt-4":
        return "gpt-4-1106-preview"
    elif target == "gpt-4-1106-preview":
        return target
    return result



def is_ai_temp_supported_func(target):
    result = TEMPERATURE
    if 1.0 >= target >= 0.0:
        return target
    return result
