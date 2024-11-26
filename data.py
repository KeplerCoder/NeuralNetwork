import json


class Data:
    """
    Класс Data предназначен для работы с набором данных, таких как изображения игрального кубика или других рукописных цифр.
    Он загружает данные из JSON файла и предоставляет их для использования в моделях машинного обучения.

    Атрибуты класса:
    - data_number: Номер текущего изображения, которое используется для анализа.
    - data_name: Ключ в JSON файле, указывающий на необходимый набор данных.
    - file_path: Путь к файлу JSON, содержащему данные.
    - dataset: Загруженные данные из указанного файла JSON.

    Методы:
    - get_data_dict(): Возвращает словарь данных, где ключи - порядковые номера изображений.
    - get_data_sample(): Возвращает данные для текущего изображения.
    - get_normalized_target_value(): Возвращает нормированное значение целевого объекта.
    """

    data_name: str = 'cube'
    data_class_name = 1
    data_number: int = 1
    file_path: str = 'encoded_images.json'
    dataset: dict[str, any]

    try:
        with open(file_path, 'r') as f:
            dataset = json.load(f)
    except FileNotFoundError:
        raise ValueError(f'Файл не найден: {file_path}')
    except json.JSONDecodeError:
        raise ValueError(f'Ошибка декодирования JSON в файле: {file_path}')

    @classmethod
    def get_data_dict(cls) -> dict[int, any]:
        """
        Возвращает словарь данных.
        :return: Словарь с данными, где ключи - порядковые номера классов изображений.
        """
        return dict(list(enumerate(cls.dataset[cls.data_name].get(str(cls.data_class_name), []), 1)))

    def get_data_sample(self) -> any:
        """
        Возвращает данные для текущего изображения.
        :return: Данные для текущего изображения.
        """
        result = self.get_data_dict().get(self.data_number)
        if result is None:
            raise ValueError(
                f'Номер изображения {self.data_number} или '
                f'номер класса изображений {self.data_class_name} за пределами диапазона!'
            )
        return result

    def get_normalized_target_value(self, data_number: int) -> float:
        """
        Возвращает нормированное значение целевого объекта изображений.
        :param data_number: Номер данных, для которых нужно нормированное значение.
        :return: Нормированное значение целевого объекта.
        """
        data_dict = [key for key in self.get_data_dict()]
        return data_dict[data_number - 1] / 10

    def get_target_value_by_key(self, value_by_key: str) -> float:
        """
        Возвращает значение целевого объекта на основе ключа словаря.

        :param value_by_key: Ключ словаря данных.
        :return: Целевое значение целевого объекта.
        """
        target_values = {
            key: float(key) / 10 for key in self.dataset[self.data_name]
        }
        return target_values.get(value_by_key, 0.0)
