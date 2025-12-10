#!/usr/bin/env python3
"""
Скрипт для запуска и проверки Ollama
"""
import subprocess
import time
import sys
import requests

def check_ollama_running():
    """Проверка, запущен ли Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_ollama():
    """Запуск Ollama сервера"""
    print("🚀 Запуск Ollama сервера...")
    
    # Проверяем, не запущен ли уже сервер
    if check_ollama_running():
        print("✅ Ollama уже запущен")
        return True
    
    # Запускаем сервер в фоновом режиме
    try:
        # Для Linux/Mac
        if sys.platform != "win32":
            process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            # Для Windows
            process = subprocess.Popen(
                ["ollama", "serve"],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        print("⏳ Ожидание запуска Ollama...")
        
        # Ждем до 30 секунд
        for i in range(30):
            if check_ollama_running():
                print("✅ Ollama успешно запущен")
                return True
            time.sleep(1)
        
        print("❌ Не удалось запустить Ollama за 30 секунд")
        return False
        
    except FileNotFoundError:
        print("❌ Ollama не установлен")
        print("Установите Ollama с https://ollama.ai/download")
        return False
    except Exception as e:
        print(f"❌ Ошибка при запуске Ollama: {e}")
        return False

def pull_model(model_name="mistral"):
    """Загрузка модели Ollama"""
    print(f"📥 Загрузка модели '{model_name}'...")
    
    try:
        # Проверяем, есть ли уже модель
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            if any(m["name"].startswith(model_name) for m in models):
                print(f"✅ Модель '{model_name}' уже загружена")
                return True
        
        # Загружаем модель
        print(f"⏳ Загрузка модели, это может занять несколько минут...")
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Модель '{model_name}' успешно загружена")
            return True
        else:
            print(f"❌ Ошибка при загрузке модели: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def setup_ollama():
    """Полная настройка Ollama"""
    print("=" * 60)
    print("НАСТРОЙКА OLLAMA ДЛЯ АНАЛИЗА ТЕКСТОВ")
    print("=" * 60)
    
    # 1. Запускаем сервер
    if not start_ollama():
        return False
    
    # 2. Загружаем модель
    # Можно выбрать другую модель: "llama2", "llama3", "russian-llama"
    model = "mistral"
    if not pull_model(model):
        # Пробуем альтернативную модель
        print("\n🔄 Пробуем альтернативную модель 'llama2'...")
        model = "llama2"
        if not pull_model(model):
            return False
    
    print(f"\n✅ Настройка завершена!")
    print(f"📖 Используемая модель: {model}")
    print(f"🔗 API доступен по: http://localhost:11434")
    print("\nТеперь можно запускать анализ текстов через LLM!")
    
    return True

if __name__ == "__main__":
    setup_ollama()