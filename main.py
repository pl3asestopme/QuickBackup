import os
import time
import sys
import zipfile
import tarfile
import logging

# Список файлов и каталогов для резервного копирования
source = []

# Основной каталог для хранения резервных копий
target_dir = os.path.expanduser('~/Backups')

# Настройка логирования
log_file = os.path.join(target_dir, "backup_log.txt")
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Проверка и создание каталога Backups, если он не существует
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    logging.info(f'Создана папка для резервных копий: {target_dir}')
    print(f'Создана папка для резервных копий: {target_dir}')

# Текущая дата для папки архива
today = target_dir + os.sep + time.strftime('%Y-%m-%d')
now = time.strftime('%H-%M-%S')

# Создание папки для сегодняшнего дня, если она не существует
if not os.path.exists(today):
    os.makedirs(today)
    logging.info(f'Создана папка для резервного копирования на сегодня: {today}')
    print(f'Создана папка для резервного копирования на сегодня: {today}')

def format_size(size):
    """Возвращает строку с размером файла в байтах, КБ и МБ."""
    size_in_bytes = f"{size} байт"
    size_in_kb = f"{size / 1024:.2f} КБ"
    size_in_mb = f"{size / (1024 * 1024):.2f} МБ"
    return f"{size_in_bytes} | {size_in_kb} | {size_in_mb}"

def display_source_list():
    """Выводит список файлов и папок, которые будут добавлены в архив."""
    print("\nФайлы и каталоги, которые будут добавлены в архив:")
    for item in source:
        logging.info(f"Добавлен в резервную копию: {item}")
        print(f" - {item}")

def add_files():
    global current_dir
    items = os.listdir(current_dir)
    
    print("\nСодержимое каталога:", current_dir)
    
    folders = [item for item in items if os.path.isdir(os.path.join(current_dir, item))]
    files = [item for item in items if os.path.isfile(os.path.join(current_dir, item))]

    print("\nПапки:")
    for i, folder in enumerate(folders):
        print(f"{i + 1}. {folder}")

    print("\nФайлы:")
    for i, file in enumerate(files):
        print(f"{i + len(folders) + 1}. {file}")

    print(f'Выберите номер элемента для перехода или добавления в архив, "0" для возврата, "q" для выхода --> ', end='')
    
    choice = input().strip()

    if choice == 'q':
        logging.info("Завершение программы по запросу пользователя.")
        exit()
    elif choice == '0':
        parent_dir = os.path.dirname(current_dir)
        if parent_dir != current_dir:
            current_dir = parent_dir
        else:
            print("Вы находитесь в корневом каталоге. Невозможно вернуться выше.")
        add_files()
    else:
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(folders):
                folder_name = folders[choice_index]
                folder_path = os.path.join(current_dir, folder_name)
                while True:
                    action = input(f'Вы хотите скопировать папку "{folder_name}" или зайти в нее? (копировать/зайти) --> ').strip().lower()
                    if action == 'копировать':
                        source.append(folder_path)
                        logging.info(f"Добавлена папка для резервного копирования: {folder_path}")
                        print(f"Папка {folder_path} добавлена в резервную копию.")
                        break
                    elif action == 'зайти':
                        current_dir = folder_path
                        add_files()
                        return
                    else:
                        print("Пожалуйста, введите корректный ответ (копировать/зайти).")
                
                while True:
                    add_more = input("Хотите добавить еще файлы или папки? (да/нет) --> ").strip().lower()
                    if add_more in ('да', 'yes'):
                        add_files()
                        return
                    elif add_more in ('нет', 'no'):
                        return
                    else:
                        print("Корректно введите ответ на вопрос (да/нет).")

            elif len(folders) <= choice_index < len(folders) + len(files):
                file_to_add = os.path.join(current_dir, files[choice_index - len(folders)])
                if file_to_add in source:
                    print("Файл который вы пытаетесь выбрать уже ВЫБРАН")
                else:
                    source.append(file_to_add)
                    logging.info(f"Добавлен файл для резервного копирования: {file_to_add}")
                    print(f"Файл {file_to_add} добавлен в резервную копию.")

                while True:
                    add_more = input("Хотите добавить еще файлы или папки? (да/нет) --> ").strip().lower()
                    if add_more in ('да', 'yes'):
                        add_files()
                        return
                    elif add_more in ('нет', 'no'):
                        return
                    else:
                        print("Корректно введите ответ на вопрос (да/нет).")
            else:
                print("Некорректный выбор, попробуйте снова.")
                add_files()
        except ValueError:
            print("Пожалуйста, введите число.")
            add_files()

# Устанавливаем начальный каталог
current_dir = os.path.expanduser('~')
add_files()

# Итоговый вывод списка файлов и подтверждение
while True:
    display_source_list()  # Выводим текущий список перед вопросом
    while True:
        confirm = input("\nСогласны с этим списком? (да/нет) --> ").strip().lower()
        if confirm in ('да', 'yes'):
            logging.info("Пользователь подтвердил список файлов для резервного копирования.")
            # Запрос выбора формата архива с проверкой
            while True:
                archive_format = input('Выберите формат архива (zip/tar) --> ').strip().lower()
                if archive_format in ('zip', 'tar'):
                    logging.info(f"Выбран формат архива: {archive_format}")
                    break  # Корректный формат, выходим из цикла
                else:
                    print("Неподдерживаемый формат архива. Пожалуйста, выберите zip или tar.")

            # Запрос комментария у пользователя
            comment = input('Введите комментарий --> ')

            # Формирование имени файла архива
            if len(comment) == 0:
                target_name = now
            else:
                target_name = now + '_' + comment.replace(' ', '_')

            # Создание архива в выбранном формате
            if archive_format == 'zip':
                target = today + os.sep + target_name + '.zip'
                with zipfile.ZipFile(target, 'w') as zipf:
                    for file in source:
                        zipf.write(file, os.path.relpath(file, start=os.path.dirname(file)))
                logging.info(f'ZIP архив успешно создан: {target}')
                print(f'ZIP архив успешно создан: {target}')
            elif archive_format == 'tar':
                target = today + os.sep + target_name + '.tar.gz'
                with tarfile.open(target, 'w:gz') as tarf:
                    for file in source:
                        tarf.add(file, arcname=os.path.relpath(file, start=os.path.dirname(file)))
                logging.info(f'TAR архив успешно создан: {target}')
                print(f'TAR архив успешно создан: {target}')

            # Вычисление размеров файлов
            original_size = sum(os.path.getsize(f) for f in source)
            archive_size = os.path.getsize(target)
            compression_ratio = (1 - archive_size / original_size) * 100

            # Вывод информации о размерах
            logging.info(f"Исходный размер файлов: {format_size(original_size)}")
            logging.info(f"Размер архива: {format_size(archive_size)}")
            logging.info(f"Сжатие: {compression_ratio:.2f}%")
            print(f"Исходный размер файлов: {format_size(original_size)}")
            print(f"Размер архива: {format_size(archive_size)}")
            print(f"Сжатие: {compression_ratio:.2f}%")

            # Завершение резервного копирования
            logging.info("Резервное копирование завершено успешно.")
            print("Резервное копирование завершено успешно.")
            break  # Выход из внутреннего цикла после успешного создания архива

        elif confirm in ('нет', 'no'):
            # Логируем отказ от подтверждения списка
            logging.info("Пользователь отказался от подтверждения списка файлов для резервного копирования.")
            
            # Спросить, хочет ли пользователь добавить еще файлы
            while True:
                add_more = input("Хотите добавить еще файлы или папки? (да/нет/вернуться) --> ").strip().lower()
                if add_more in ('да', 'yes'):
                    logging.info("Пользователь выбрал добавление дополнительных файлов.")
                    add_files()  # Добавить файлы
                    break  # Выход из внутреннего цикла и обновление списка
                elif add_more in ('нет', 'no'):
                    # Спросить, хочет ли пользователь прервать резервное копирование
                    cancel = input("Хотите прервать резервное копирование? (да/нет) --> ").strip().lower()
                    if cancel in ('да', 'yes'):
                        logging.info("Пользователь отменил резервное копирование.")
                        print("Резервное копирование отменено.")
                        sys.exit()  # Завершение программы
                    elif cancel in ('нет', 'no'):
                        logging.info("Пользователь решил продолжить выбор файлов.")
                        continue
                elif add_more == 'вернуться':
                    # Повторно вывести список и вернуться к вопросу о согласии
                    logging.info("Пользователь вернулся к выбору подтверждения списка файлов.")
                    display_source_list()  # Обновляем вывод перед повторным вопросом
                    break  # Выход из внутреннего цикла
                else:
                    print("Пожалуйста, введите корректный ответ (да/нет/вернуться).")
        else:
            print("Корректно введите ответ на вопрос (да/нет).")
    break  # Выход из внешнего цикла после успешного создания архива

