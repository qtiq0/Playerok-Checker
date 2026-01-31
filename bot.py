import sys
import os
import time
import json
import curl_cffi
from typing import List, Dict, Any
from datetime import datetime
import threading
from queue import Queue


class Color:
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_CYAN = "\033[96m"


class Printer:
    @staticmethod
    def print_color(text: str, color: str, end: str = "\n"):
        print(f"{color}{text}{Color.RESET}", end=end)
    
    @staticmethod
    def success(text: str):
        Printer.print_color(f"[+] {text}", Color.GREEN)
    
    @staticmethod
    def error(text: str):
        Printer.print_color(f"[-] {text}", Color.RED)
    
    @staticmethod
    def warning(text: str):
        Printer.print_color(f"[!] {text}", Color.YELLOW)
    
    @staticmethod
    def info(text: str):
        Printer.print_color(f"[i] {text}", Color.BRIGHT_CYAN)
    
    @staticmethod
    def system(text: str):
        Printer.print_color(f"[*] {text}", Color.BRIGHT_BLUE)


class UIHelper:
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_line(char: str = "=", length: int = 64, color: str = Color.BRIGHT_BLUE):
        Printer.print_color(char * length, color)
    
    @staticmethod
    def print_double_line(length: int = 64, color: str = Color.BRIGHT_CYAN):
        Printer.print_color("=" * length, color)
    
    @staticmethod
    def print_header(text: str):
        UIHelper.print_double_line()
        print(f"{Color.BOLD}{Color.BRIGHT_CYAN}{text.center(64)}{Color.RESET}")
        UIHelper.print_double_line()
    
    @staticmethod
    def get_input(prompt: str, default: str = "") -> str:
        Printer.print_color(f"{Color.BRIGHT_CYAN}{prompt}: {Color.RESET}", Color.YELLOW, end="")
        result = input().strip()
        return result if result else default
    
    @staticmethod
    def print_card(title: str, content: List[str]):
        width = 62
        print(f"\n{Color.BRIGHT_BLUE}+{'-' * (width - 2)}+{Color.RESET}")
        print(f"{Color.BRIGHT_BLUE}|{Color.BRIGHT_CYAN}{title.center(width - 2)}{Color.BRIGHT_BLUE}|{Color.RESET}")
        print(f"{Color.BRIGHT_BLUE}+{'-' * (width - 2)}+{Color.RESET}")
        for line in content:
            if line.strip():
                print(f"{Color.BRIGHT_BLUE}|{Color.RESET} {line.ljust(width - 4)} {Color.BRIGHT_BLUE}|{Color.RESET}")
            else:
                print(f"{Color.BRIGHT_BLUE}|{' ' * (width - 2)}|{Color.RESET}")
        print(f"{Color.BRIGHT_BLUE}+{'-' * (width - 2)}+{Color.RESET}")
    
    @staticmethod
    def loading_animation(text: str = "Загрузка"):
        chars = ["|", "/", "-", "\\"]
        for i in range(12):
            sys.stdout.write(f"\r{Color.BRIGHT_CYAN}{chars[i % len(chars)]}{Color.RESET} {text}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * 30 + "\r")


class PlayerOkAPI:
    PERSISTED_QUERIES = {
        "user": "2e2e3b656d2ba48e0b2cd5eeedf88ef70e4aabb4ac4d9d9e9b8feff343a37d98",
        "deals": "c3b623b5fe0758cf91b2335ebf36ff65f8650a6672a792a3ca7a36d270d396fb",
        "deal": "5652037a966d8da6d41180b0be8226051fe0ed1357d460c6ae348c3138a0fba3",
        "games": "b9f6675fd5923bc5c247388e8e3209c3eede460ed328dbe6a9ec8e6428d3649b",
        "game": "12e701986f07aaaf57327b1133b9a1f3050b851c99b19293adfac40cfed0e41d",
        "game_category": "d81943c23bc558591f70286ad69bb6bf7f6229d04aae39fb0a9701d78a9fd749",
        "game_category_agreements": "3ea4b047196ed9f84aa5eb652299c4bd73f2e99e9fdf4587877658d9ea6330f6",
        "game_category_obtaining_types": "15b0991414821528251930b4c8161c299eb39882fd635dd5adb1a81fb0570aea",
        "game_category_instructions": "5991cead6a8ca46195bc4f7ae3164e7606105dbb82834c910658edeb0a1d1918",
        "game_category_data_fields": "6fdadfb9b05880ce2d307a1412bc4f2e383683061c281e2b65a93f7266ea4a49",
        "chats": "f7e6ee4fbb892abbd196342110e2abb0be309e2bd6671abb2963d0809c511d05",
        "chat": "bb024dc0652fc7c1302a64a117d56d99fb0d726eb4b896ca803dca55f611d933",
        "chat_messages": "e8162a8500865f4bb18dbaacb1c4703823f74c1925a91a5103f41c2021f0557a",
        "items": "206ae9d63e58bc41df9023aae39b9136f358282a808c32ee95f5b8b6669a8c8b",
        "item": "5b2be2b532cea7023f4f584512c4677469858e2210349f7eec78e3b96d563716",
        "item_priority_statuses": "b922220c6f979537e1b99de6af8f5c13727daeff66727f679f07f986ce1c025a",
        "transaction_providers": "31960e5dd929834c1f85bc685db80657ff576373076f016b2578c0a34e6e9f42",
        "transactions": "3b9925106c3fe9308ac632254fd70da347b5701f243ab8690477d5a7ca37c2c8",
        "sbp_bank_members": "ef7902598e855fa15fb5e3112156ac226180f0b009a36606fc80a18f00b80c63",
        "verified_cards": "eb338d8432981307a2b3d322b3310b2447cab3a6acf21aba4b8773b97e72d1aa"
    }


class APIException(Exception):
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class Account:
    def __init__(self, token: str, timeout: int = 10, proxy: str = None):
        self.token = token
        self.timeout = timeout
        self.proxy = proxy
        self.base_url = "https://playerok.com"
        
        self._user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self._curl_session = curl_cffi.Session(
            impersonate="chrome",
            timeout=timeout,
            proxy=proxy
        )
        
        self.id = None
        self.username = None
        self.email = None
        self.balance = 0.0
        self.is_blocked = False
        self.profile = None

    def _request(self, method: str, endpoint: str, data: dict = None, headers: dict = None):
        url = f"{self.base_url}{endpoint}"
        default_headers = {
            "accept": "*/*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/json",
            "cookie": f"token={self.token}",
            "origin": "https://playerok.com",
            "referer": "https://playerok.com/",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": self._user_agent,
            "x-timezone-offset": "-240"
        }
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = self._curl_session.get(url, params=data, headers=default_headers)
            else:
                response = self._curl_session.post(url, json=data, headers=default_headers)
            
            if response.status_code != 200:
                raise APIException(f"HTTP {response.status_code}", response.status_code)
            
            return response.json()
        except Exception as e:
            raise APIException(str(e))

    def get(self):
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "viewer",
            "query": """
            query viewer {
              viewer {
                ...Viewer
                __typename
              }
            }
            fragment Viewer on User {
              id
              username
              email
              role
              hasFrozenBalance
              supportChatId
              systemChatId
              unreadChatsCounter
              isBlocked
              isBlockedFor
              createdAt
              lastItemCreatedAt
              hasConfirmedPhoneNumber
              canPublishItems
              profile {
                id
                avatarURL
                testimonialCounter
                __typename
              }
              __typename
            }
            """,
            "variables": {}
        }
        
        response = self._request("POST", "/graphql", payload, headers)
        
        if "errors" in response:
            error_msg = response["errors"][0]["message"]
            raise APIException(error_msg)
        
        data = response.get("data", {}).get("viewer")
        if not data:
            raise APIException("Нет данных аккаунта")
        
        self.id = data.get("id")
        self.username = data.get("username")
        self.email = data.get("email")
        self.is_blocked = data.get("isBlocked", False)
        self.profile = data.get("profile", {})
        
        user_payload = {
            "operationName": "user",
            "variables": json.dumps({"username": self.username, "hasSupportAccess": False}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": PlayerOkAPI.PERSISTED_QUERIES["user"]}}, ensure_ascii=False)
        }
        
        user_response = self._request("GET", "/graphql", user_payload, headers)
        user_data = user_response.get("data", {}).get("user", {})
        
        if user_data.get("__typename") == "User":
            balance_data = user_data.get("balance", {})
            self.balance = float(balance_data.get("available", 0)) if balance_data else 0.0
        
        return self


class TokenManager:
    @staticmethod
    def load_tokens(filename: str = "tokens.txt") -> List[str]:
        if not os.path.exists(filename):
            return []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                tokens = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            return tokens
        except:
            return []
    
    @staticmethod
    def save_valid_tokens(tokens: List[Dict[str, Any]], filename: str = "valid_tokens.json"):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(tokens, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    @staticmethod
    def format_balance(balance: float) -> str:
        try:
            return f"{balance:,.2f} ₽".replace(",", " ")
        except:
            return "0.00 ₽"


class TokenChecker:
    def __init__(self, tokens: List[str], results_queue: Queue, thread_id: int):
        self.tokens = tokens
        self.results_queue = results_queue
        self.thread_id = thread_id
    
    def run(self):
        for token in self.tokens:
            try:
                account = Account(token, timeout=7)
                account.get()
                balance = TokenManager.format_balance(account.balance)
                
                self.results_queue.put({
                    'type': 'valid',
                    'token': token[:10] + "...",
                    'username': account.username,
                    'balance': balance,
                    'email': account.email or 'Не указан',
                    'status': 'АКТИВЕН' if not account.is_blocked else 'ЗАБЛОКИРОВАН',
                    'thread': self.thread_id
                })
            except:
                self.results_queue.put({
                    'type': 'invalid',
                    'token': token[:10] + "...",
                    'thread': self.thread_id
                })


class PlayerOkChecker:
    def __init__(self):
        self.stats = {
            'checked': 0,
            'valid': 0,
            'invalid': 0,
            'start_time': None,
            'total_balance': 0.0
        }
    
    def show_banner(self):
        UIHelper.clear_screen()
        print(f"{Color.BRIGHT_BLUE}{Color.BOLD}")
        print("================================================================")
        print("                     PLAYEROK TOKEN CHECKER PRO                 ")
        print("                           Версия 3.0                           ")
        print("================================================================\n")
        print(Color.RESET)
        print(f"{Color.BRIGHT_CYAN}")
        print("           Автоматизированная система проверки")
        print("           Оптимизированная многопоточная архитектура")
        print("           Разработано qitq0")
        print(Color.RESET)
        UIHelper.print_line("=", 64, Color.BRIGHT_BLUE)
        print(f"{Color.BRIGHT_CYAN}           Текущее время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}{Color.RESET}")
        UIHelper.print_line("=", 64, Color.BRIGHT_BLUE)
        print()
    
    def check_single_token(self):
        self.show_banner()
        UIHelper.print_header("ПРОВЕРКА ЕДИНИЧНОГО ТОКЕНА")
        
        token = UIHelper.get_input("Введите токен для проверки")
        if not token:
            Printer.error("Токен не может быть пустым")
            time.sleep(1)
            return
        
        UIHelper.loading_animation("Проверка токена")
        
        try:
            account = Account(token, timeout=8)
            account.get()
            
            self.show_banner()
            UIHelper.print_header("РЕЗУЛЬТАТ ПРОВЕРКИ")
            
            balance = TokenManager.format_balance(account.balance)
            status = "АКТИВЕН" if not account.is_blocked else "ЗАБЛОКИРОВАН"
            status_color = Color.GREEN if not account.is_blocked else Color.RED
            
            info = [
                f"Никнейм:       {account.username}",
                f"Баланс:        {balance}",
                f"Email:         {account.email or 'Не указан'}",
                f"Статус:        {status_color}{status}{Color.RESET}",
                f"ID аккаунта:   {account.id or 'Неизвестно'}",
                f"Проверено:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ]
            
            UIHelper.print_card("ИНФОРМАЦИЯ О АККАУНТЕ", info)
            
            self.stats['checked'] += 1
            self.stats['valid'] += 1
            self.stats['total_balance'] += account.balance
            
        except APIException as e:
            UIHelper.print_header("РЕЗУЛЬТАТ ПРОВЕРКИ")
            Printer.error(f"Токен невалидный: {e.message}")
            self.stats['checked'] += 1
            self.stats['invalid'] += 1
        except Exception as e:
            UIHelper.print_header("РЕЗУЛЬТАТ ПРОВЕРКИ")
            Printer.error(f"Ошибка проверки: {str(e)}")
            self.stats['checked'] += 1
            self.stats['invalid'] += 1
    
    def check_multiple_tokens(self):
        self.show_banner()
        UIHelper.print_header("МАССОВАЯ ПРОВЕРКА ТОКЕНОВ")
        
        tokens = TokenManager.load_tokens()
        
        if not tokens:
            Printer.error("Файл tokens.txt не найден или пуст")
            time.sleep(1)
            return
        
        Printer.system(f"Найдено токенов: {len(tokens)}")
        UIHelper.print_line("-", 64, Color.BRIGHT_CYAN)
        
        num_threads = min(8, len(tokens))
        chunk_size = len(tokens) // num_threads
        
        results_queue = Queue()
        threads = []
        
        self.stats['start_time'] = time.time()
        
        Printer.info("Запуск многопоточной проверки...")
        
        for i in range(num_threads):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size if i < num_threads - 1 else len(tokens)
            thread_tokens = tokens[start_idx:end_idx]
            
            checker = TokenChecker(thread_tokens, results_queue, i + 1)
            thread = threading.Thread(target=checker.run)
            thread.daemon = True
            threads.append(thread)
            thread.start()
        
        valid_tokens = []
        invalid_count = 0
        processed = 0
        
        print(f"\n{Color.BRIGHT_CYAN}Прогресс проверки:{Color.RESET}\n")
        
        while processed < len(tokens):
            result = results_queue.get()
            processed += 1
            
            progress = (processed / len(tokens)) * 100
            bar_length = 30
            filled = int(bar_length * processed // len(tokens))
            bar = f"{Color.BRIGHT_BLUE}#{Color.GREEN}" * filled + f"{Color.BRIGHT_BLUE}.{Color.RESET}" * (bar_length - filled)
            
            sys.stdout.write(f"\r[{bar}] {progress:.1f}% ({processed}/{len(tokens)})")
            sys.stdout.flush()
            
            if result['type'] == 'valid':
                valid_tokens.append({
                    'token': result['token'],
                    'username': result['username'],
                    'balance': result['balance'],
                    'email': result['email'],
                    'status': result['status']
                })
            else:
                invalid_count += 1
        
        for thread in threads:
            thread.join(timeout=2)
        
        elapsed_time = time.time() - self.stats['start_time']
        
        print("\n")
        UIHelper.print_header("ИТОГИ ПРОВЕРКИ")
        
        total_balance = sum(float(t['balance'].replace(' ₽', '').replace(' ', '').replace(',', '')) 
                          for t in valid_tokens if ' ₽' in t['balance'])
        
        results = [
            f"Всего проверено:    {len(tokens)}",
            f"Валидных токенов:   {len(valid_tokens)}",
            f"Невалидных токенов: {invalid_count}",
            f"Общий баланс:       {TokenManager.format_balance(total_balance)}",
            f"Время выполнения:   {elapsed_time:.2f} сек",
            f"Скорость проверки:  {len(tokens)/elapsed_time:.1f} токенов/сек" if elapsed_time > 0 else ""
        ]
        
        UIHelper.print_card("СТАТИСТИКА ПРОВЕРКИ", results)
        
        if valid_tokens:
            UIHelper.print_header("ВАЛИДНЫЕ ТОКЕНЫ")
            
            token_list = []
            for i, token_info in enumerate(valid_tokens[:15], 1):
                username_display = token_info['username'][:20] + "..." if len(token_info['username']) > 20 else token_info['username']
                token_list.append(f"{i:2}. {username_display:<23} {token_info['balance']:<12}")
            
            if len(valid_tokens) > 15:
                token_list.append(f"... и еще {len(valid_tokens) - 15} токенов")
            
            UIHelper.print_card("СПИСОК АККАУНТОВ", token_list)
            
            save_choice = UIHelper.get_input("\nСохранить результаты в файл? (y/n)", "n")
            if save_choice.lower() == 'y':
                if TokenManager.save_valid_tokens(valid_tokens):
                    Printer.success("Результаты успешно сохранены в valid_tokens.json")
                else:
                    Printer.error("Ошибка сохранения файла")
        
        self.stats['checked'] += len(tokens)
        self.stats['valid'] += len(valid_tokens)
        self.stats['invalid'] += invalid_count
        self.stats['total_balance'] += total_balance
    
    def show_help(self):
        self.show_banner()
        UIHelper.print_header("СПРАВКА И ИНСТРУКЦИИ")
        
        help_content = [
            "ПОЛУЧЕНИЕ ТОКЕНА:",
            "1. Установите расширение Cookie Editor",
            "2. Авторизуйтесь на playerok.com",
            "3. Откройте Cookie Editor",
            "4. Найдите куку 'token' для playerok.com",
            "5. Скопируйте значение токена",
            "",
            "МАССОВАЯ ПРОВЕРКА:",
            "Создайте файл tokens.txt в папке с программой",
            "Каждый токен на отдельной строке",
            "Комментарии начинаются с #",
            "",
            "ФОРМАТ ФАЙЛА:",
            "# Комментарий",
            "ваш_токен_1",
            "ваш_токен_2",
            "# Еще один токен",
            "ваш_токен_3",
            "",
            "СТАТИСТИКА:",
            f"Проверено: {self.stats['checked']}",
            f"Валидных: {self.stats['valid']}",
            f"Невалидных: {self.stats['invalid']}",
            f"Общий баланс: {TokenManager.format_balance(self.stats['total_balance'])}",
            "",
            "ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ:",
            "Версия: 3.0",
            "Архитектура: Многопоточная",
            "Разработчик: qitq0",
            "Контакты: @qtiq0"
        ]
        
        UIHelper.print_card("РУКОВОДСТВО ПОЛЬЗОВАТЕЛЯ", help_content)
    
    def show_stats(self):
        self.show_banner()
        UIHelper.print_header("СТАТИСТИКА СИСТЕМЫ")
        
        if self.stats['checked'] > 0:
            efficiency = self.stats['valid'] / self.stats['checked'] * 100
        else:
            efficiency = 0
        
        avg_balance = self.stats['total_balance'] / self.stats['valid'] if self.stats['valid'] > 0 else 0
        
        stats_content = [
            "ОБЩАЯ СТАТИСТИКА:",
            "",
            f"Всего проверок:    {self.stats['checked']}",
            f"Успешных проверок: {self.stats['valid']}",
            f"Неудачных проверок: {self.stats['invalid']}",
            f"Эффективность:     {efficiency:.1f}%",
            "",
            "ФИНАНСОВАЯ СТАТИСТИКА:",
            f"Общий баланс:      {TokenManager.format_balance(self.stats['total_balance'])}",
            f"Средний баланс:    {TokenManager.format_balance(avg_balance)}",
            "",
            "СИСТЕМНАЯ ИНФОРМАЦИЯ:",
            f"Последняя активность: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
            f"Версия программы: 3.0 Pro",
            f"Разработчик: qitq0"
        ]
        
        UIHelper.print_card("АНАЛИТИЧЕСКИЕ ДАННЫЕ", stats_content)
    
    def show_menu(self):
        while True:
            self.show_banner()
            
            menu_items = [
                "Проверить один токен",
                "Массовая проверка токенов",
                "Справочная информация",
                "Статистика системы",
                "Выход из программы"
            ]
            
            print(f"{Color.BOLD}{Color.BRIGHT_CYAN}ОСНОВНОЕ МЕНЮ{Color.RESET}")
            UIHelper.print_double_line()
            
            for i, item in enumerate(menu_items, 1):
                print(f"  {Color.BRIGHT_BLUE}[{i}]{Color.RESET} {item}")
            
            UIHelper.print_double_line()
            print()
            
            choice = UIHelper.get_input("Выберите действие (1-5)", "1")
            
            if choice == '1':
                self.check_single_token()
                UIHelper.get_input("\nНажмите Enter для продолжения", "")
            elif choice == '2':
                self.check_multiple_tokens()
                UIHelper.get_input("\nНажмите Enter для продолжения", "")
            elif choice == '3':
                self.show_help()
                UIHelper.get_input("\nНажмите Enter для продолжения", "")
            elif choice == '4':
                self.show_stats()
                UIHelper.get_input("\nНажмите Enter для продолжения", "")
            elif choice == '5':
                Printer.system("Завершение работы программы...")
                UIHelper.print_double_line()
                print(f"{Color.BOLD}Спасибо за использование PlayerOk Checker Pro!{Color.RESET}")
                UIHelper.print_double_line()
                time.sleep(1)
                break
            else:
                Printer.error("Неверный выбор. Введите число от 1 до 5")
                time.sleep(1)
    
    def run(self):
        try:
            self.show_banner()
            
            try:
                import curl_cffi
                Printer.success("Системные зависимости проверены")
            except ImportError:
                Printer.error("Модуль curl-cffi не установлен")
                Printer.warning("Установите: pip install curl-cffi")
                UIHelper.get_input("\nНажмите Enter для выхода", "")
                return
            
            UIHelper.loading_animation("Инициализация системы")
            
            self.show_menu()
            
        except KeyboardInterrupt:
            print(f"\n\n{Color.YELLOW}Работа программы прервана{Color.RESET}")
            time.sleep(1)
        except Exception as e:
            Printer.error(f"Системная ошибка: {e}")
            UIHelper.get_input("\nНажмите Enter для выхода", "")


def main():
    checker = PlayerOkChecker()
    checker.run()


if __name__ == "__main__":
    main()
