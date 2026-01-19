import re
from datetime import datetime
from collections import Counter

class DocumentParser:
    def parse(self, text):
        """
        Парсит документ в формате пользователя:
        Структура:
        1. Заголовок статьи (без 5 пробелов в начале)
        2. Текст статьи (начинается с 5 пробелов, продолжается до следующего заголовка)
        3. Следующий заголовок (без 5 пробелов в начале)
        И так далее.
        """
        lines = text.split('\n')
        #print(f"Всего строк в документе: {len(lines)}")
        
        lines = [line.replace('\r', '') for line in lines]
        
        # Отладка: 
        #print("\nСтроки документа:")
        #for i, line in enumerate(lines):
            #print(f"{i:3}: {repr(line)}")
        
        content_start = None
        
        i_start = 0
        i = 0
        while i < len(lines)-2:

            if lines[i] == "":
                print("OK1")
                if lines[i+1] == "      ":
                    print("OK2")
                    i_start = i + 2
                    break
            i += 1
        for i in range(i_start, len(lines)):
            if 'ПОИСК ДОКУМЕНТОВ' in lines[i] or 'ОГЛАВЛЕНИЕ' in lines[i] or '\t' in lines[i]:
                continue
            if lines[i].strip() and not lines[i].startswith('     '):
                content_start = i
                print(f"\nНачало статей на строке {content_start}: {lines[content_start]}")
                break
        
        if content_start is None:
            print("Не удалось найти начало статей!")
            return []
        
        articles = []
        i = content_start
        while i < len(lines):
            if not lines[i].strip():
                i += 1
                continue
            
            
            if lines[i] == " Параметры поискового запроса":
                break
            
            

            if "Язык оригинала" in lines[i]:
                articles[len(articles)-1]['title'] += lines[i] + lines[i + 1]
                articles[len(articles)-1]['content'] += lines[i] + lines[i + 2]   
                articles[len(articles)-1]['raw_text'] += lines[i] + lines[i + 2] 

                #print(articles[len(articles)-1]['title'])

                i += 3
                continue 

            article_title = lines[i]
            article_lines = lines[i+1]
            articles.append({
                        'title': article_title,
                        'content': article_lines,
                        'raw_text': article_lines
                    })
            
            

            i += 2
       # print(f"\nНайдено статей: {len(articles)}")
        
        #for idx, article in enumerate(articles):
            #print(f"\n{'='*60}")
            #print(f"Статья {idx + 1}:")
            #print(f"Заголовок: {article['title']}")
            #print(f"Длина текста: {len(article['content'])} символов")
            #print(f"Первые 200 символов текста:")
            #if article['content']:
                #print(article['content'][:200] + '...' if len(article['content']) > 200 else article['content'])
            #else:
                #print("(текст отсутствует)")
            #print(f"{'='*60}")
        
        return articles


class TextAnalyzer:
    def __init__(self):
        pass
    
    def extract_metadata(self, text):
        """Извлекает метаданные из конца текста"""
        last_open_bracket = text.rfind('(')
        last_close_bracket = text.rfind(')')
        
        if last_open_bracket == -1 or last_close_bracket == -1 or last_close_bracket < last_open_bracket:
            return {
                'publisher': None,
                'date_raw': None,
                'event_types': None,
                'clean_text': text.strip()
            }
        
        metadata_str = text[last_open_bracket + 1:last_close_bracket].strip()
        
        clean_text = text[:last_open_bracket].strip()
        
        pattern = r'^([^,]+),\s*([^,]+)(?:,\s*типы событий:\s*(.+))?$'
        match = re.search(pattern, metadata_str, re.IGNORECASE)
        
        if match:
            publisher = match.group(1).strip()
            date_raw = match.group(2).strip()
            
            if match.group(3):
                event_types = match.group(3).strip()
                event_types = re.sub(r'[«»"\']', '', event_types)
                
                if event_types.lower() == 'нет':
                    event_types = None
            else:
                event_types = None
            
            return {
                'publisher': publisher,
                'date_raw': date_raw,
                'event_types': event_types,
                'clean_text': clean_text
            }
        
        parts = [part.strip() for part in metadata_str.split(',')]
        
        if len(parts) >= 2:
            publisher = parts[0]
            date_raw = parts[1]
            event_types = None
            
            if len(parts) > 2:
                remaining = ','.join(parts[2:])
                types_match = re.search(r'типы событий:\s*(.+)', remaining, re.IGNORECASE)
                if types_match:
                    event_types = types_match.group(1).strip()
                    event_types = re.sub(r'[«»"\']', '', event_types)
                    if event_types.lower() == 'нет':
                        event_types = None
            
            return {
                'publisher': publisher,
                'date_raw': date_raw,
                'event_types': event_types,
                'clean_text': clean_text
            }
        
        return {
            'publisher': None,
            'date_raw': None,
            'event_types': None,
            'clean_text': clean_text
        }
    
    def parse_date(self, date_str):
        """Парсит дату из строки"""
        if not date_str:
            return {'raw': 'Дата не найдена', 'parsed': None}
        
        date_str = date_str.strip()
        
        month_map = {
            'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4,
            'май': 5, 'июн': 6, 'июл': 7, 'авг': 8,
            'сен': 9, 'окт': 10, 'ноя': 11, 'дек': 12,
            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
            'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
            'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
        }
        
        try:
            match = re.search(r'(\d{1,2})\s+([а-я]+)\s+(\d{4})', date_str, re.IGNORECASE)
            if match:
                day = int(match.group(1))
                month_str = match.group(2).lower()
                year = int(match.group(3))
                
                month = None
                for key, value in month_map.items():
                    if month_str.startswith(key):
                        month = value
                        break
                
                if month:
                    return {
                        'raw': date_str,
                        'parsed': datetime(year, month, day).strftime('%Y-%m-%d')
                    }
            
            match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', date_str)
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3))
                return {
                    'raw': date_str,
                    'parsed': datetime(year, month, day).strftime('%Y-%m-%d')
                }
                
        except Exception as e:
            print(f"Ошибка парсинга даты '{date_str}': {e}")
        
        return {'raw': date_str, 'parsed': None}
    
    def extract_persons(self, text):
        """Извлекает имена людей из текста"""
        pattern = r'\b([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)\b'
        matches = re.findall(pattern, text)
        
        common_words = {
            'России', 'Россия', 'Москва', 'Подмосковье', 'Область', 'Район',
            'Город', 'Улица', 'Проспект', 'Площадь', 'Сегодня', 'Вчера',
            'Завтра', 'Московская', 'Санкт', 'Петербург', 'Интернет', 'Издание',
            'Иностранцы', 'Туристических', 'Краснодарский', 'Ставропольский',
            'Тюменская', 'Свердловская', 'Приморский', 'Татарстан', 'Крым',
            'Костромской', 'Мурманской', 'Пермском', 'Сосногорском'
        }
        
        persons = []
        for match in matches:
            words = match.split()
            if all(word not in common_words for word in words):
                persons.append(match)
        
        return list(set(persons))[:10]
    
    def extract_keywords(self, text):
        """Извлекает ключевые слова с тональностью"""
        words = re.findall(r'\b[а-яё]{3,}\b', text.lower())
        
        stop_words = {
            'который', 'этот', 'очень', 'также', 'после', 'перед', 'через',
            'около', 'более', 'менее', 'только', 'можно', 'нужно', 'должен',
            'могут', 'будет', 'есть', 'были', 'было', 'этого', 'ему',
            'такой', 'такие', 'такое', 'такая', 'своей', 'своего', 'своих',
            'может', 'должны', 'много', 'мало', 'ещё', 'уже', 'это', 'все',
            'что', 'как', 'для', 'на', 'по', 'из', 'от', 'до', 'не', 'но',
            'за', 'же', 'ли', 'бы', 'то', 'вот', 'там', 'тут', 'где', 'когда'
        }
        
        words = [w for w in words if w not in stop_words]
        word_freq = Counter(words)
        
        positive_words = {
            'хорошо', 'отлично', 'прекрасно', 'успех', 'успешно', 'победа',
            'развитие', 'рост', 'увеличение', 'улучшение', 'новый', 'современный',
            'качественный', 'безопасный', 'надежный', 'комфортный', 'удобный',
            'эффективный', 'результат', 'достижение', 'поздравление', 'награда',
            'открытие', 'завершение', 'успешный', 'первый', 'лучший', 'важный'
        }
        
        negative_words = {
            'проблема', 'авария', 'пожар', 'трагедия', 'смерть', 'погиб',
            'убийство', 'преступление', 'нарушение', 'штраф', 'опасный',
            'сложный', 'трудный', 'плохо', 'ужасно', 'катастрофа', 'кризис',
            'конфликт', 'война', 'нападение', 'терроризм', 'преступник',
            'аварийный', 'закрытие', 'отмена', 'провал', 'неудача', 'потеря'
        }
        
        keywords = []
        for word, freq in word_freq.most_common(15):
            if word in positive_words:
                sentiment = 'positive'
            elif word in negative_words:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            keywords.append({
                'keyword': word,
                'frequency': freq,
                'sentiment': sentiment,
                'score': freq * 0.1
            })
        
        return keywords
    
    def extract_event_type(self, metadata):
        """Определяет тип события из метаданных или текста"""
        if metadata['event_types']:
            if metadata['event_types'].lower() == 'нет':
                return self._guess_event_type(metadata['clean_text'])
            return metadata['event_types']
        
        return self._guess_event_type(metadata['clean_text'])
    
    def _guess_event_type(self, text):
        """Определяет тип события по ключевым словам в тексте"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['социологический', 'исследование', 'опрос', 'статистика', 'рост', 'увеличение']):
            return 'Социологическое исследование'
        elif any(word in text_lower for word in ['снег', 'погода', 'метео', 'покров', 'сугроб', 'оттепель', 'мороз']):
            return 'Погодные условия'
        elif any(word in text_lower for word in ['школа', 'образование', 'учитель', 'ученик', 'занятие', 'звонок']):
            return 'Образование'
        elif any(word in text_lower for word in ['туризм', 'поездка', 'турист', 'путешествие', 'направление']):
            return 'Туризм'
        elif any(word in text_lower for word in ['строительство', 'ремонт', 'открытие', 'завершение']):
            return 'Строительство/Ремонт'
        elif any(word in text_lower for word in ['пожар', 'мчс', 'спасатель']):
            return 'Пожар'
        elif any(word in text_lower for word in ['дтп', 'авария', 'автомобиль']):
            return 'ДТП'
        elif any(word in text_lower for word in ['преступление', 'убийство', 'кража']):
            return 'Преступление'
        elif any(word in text_lower for word in ['праздник', 'новый год', 'мероприятие']):
            return 'Праздничное мероприятие'
        else:
            return 'Не определено'
    
    def analyze_article(self, article):
        """Полный анализ статьи"""
        text = article['content']
        
        metadata = self.extract_metadata(text)
        date_info = self.parse_date(metadata['date_raw'])
        event_type = self.extract_event_type(metadata)
        persons = self.extract_persons(metadata['clean_text'])
        keywords = self.extract_keywords(metadata['clean_text'])
        
        return {
            'title': article['title'],
            'raw_text': text,
            'clean_text': metadata['clean_text'],
            'publisher': metadata['publisher'],
            'persons': persons,
            'keywords': keywords,
            'event_type': event_type,
            'date': date_info,
            'metadata': {
                'word_count': len(metadata['clean_text'].split()),
                'char_count': len(metadata['clean_text']),
                'publisher': metadata['publisher']
            }
        }