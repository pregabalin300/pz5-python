import aiohttp
import asyncio
import json
from datetime import datetime

# Надежные API
API_URL_1 = "https://jsonplaceholder.typicode.com/posts/1"
API_URL_2 = "https://jsonplaceholder.typicode.com/users/1"

# Ограничитель одновременных запросов (максимум 3)
sem = asyncio.Semaphore(3)

async def fetch_data(url, session):
    async with sem:
        try:
            # Таймаут 5 секунд
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"[ОШИБКА] Статус {response.status} при запросе {url}")
                    return None
        except asyncio.TimeoutError:
            print(f"[ТАЙМАУТ] Превышено время ожидания для {url}")
            return None
        except Exception as e:
            print(f"[ОШИБКА] {e} при запросе {url}")
            return None

async def get_info():
    async with aiohttp.ClientSession() as session:
        # Отправляем два запроса одновременно
        task_1 = fetch_data(API_URL_1, session)
        task_2 = fetch_data(API_URL_2, session)
        
        # Ждем выполнения обоих
        data_1, data_2 = await asyncio.gather(task_1, task_2)
        
        return {
            "info_1": data_1,
            "info_2": data_2,
            "timestamp": datetime.now().isoformat()
        }

def save_data(data, filename="result.json"):
    # Записываем данные в JSON файл
    with open(filename, "a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")

async def main():
    print("Запуск сбора данных...")
    
    for i in range(3):
        data = await get_info()
        if data:
            save_data(data)
            print(f"[{i+1}/3] Данные успешно сохранены в файл.")
            
        if i < 2:
            print("Ожидание 5 секунд перед следующим сбором...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())