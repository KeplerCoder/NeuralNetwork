import pickle
from configuration import logger
from data import Data


class MachineLearning(Data):
    @staticmethod
    def _save_weights_and_biases(weights: dict[str, list[list[float]]], biases: dict[str, list[float]]) -> None:
        """
        Сохраняет веса и смещения в файл.

        :param weights: Словарь весов, где ключи - имена слоев, значения - веса слоев.
        :param biases: Словарь смещений, где ключи - имена слоев, значения - смещения слоев.
        """
        data: dict = {'weights': weights, 'biases': biases}
        try:
            with open('weights_and_biases.pkl', 'wb') as file:
                pickle.dump(data, file)
            logger.info('Данные успешно сохранены!')
        except Exception as e:
            logger.error(f'Произошла ошибка: {e}')

    @staticmethod
    def _calculate_error(predicted: float, target: float) -> float:
        """
        Вычисляет ошибку между предсказанным и целевым значениями.

        :param predicted: Предсказанное значение.
        :param target: Целевое значение.
        :return: Ошибка в процентном соотношении.
        """
        return ((predicted - target) / target) * 100

    @staticmethod
    def _get_lasso_regularization(regularization: float, weights: list[list[float]], i: int, j: int) -> float:
        """
        Вычисляет Lasso регуляризацию для данного веса.
        Добавляет абсолютное значение величины коэффициентов как штраф к функции потерь.

        :param regularization: Параметр регуляризации.
        :param weights: Список весов.
        :param i: Индекс первой координаты веса.
        :param j: Индекс второй координаты веса.
        :return: Значение Lasso регуляризации.
        """
        return regularization * (1 if weights[i][j] > 0 else -1)

    @staticmethod
    def _get_ridge_regularization(regularization: float, weights: list[list[float]], i: int, j: int) -> float:
        """
        Вычисляет Ridge регуляризацию для данного веса.
        Добавляет квадрат величины коэффициентов как штраф к функции потерь.

        :param regularization: Параметр регуляризации.
        :param weights: Список весов.
        :param i: Индекс первой координаты веса.
        :param j: Индекс второй координаты веса.
        :return: Значение Ridge регуляризации.
        """
        return regularization * weights[i][j]

    @staticmethod
    def _calculate_gradient_descent(
            input_dataset: list[float], learning_rate: float,
            gradient: float, weights: list[list[float]], i: int, j: int
    ) -> None:
        """
        Обновляет вес с использованием градиентного спуска.

        :param input_dataset: Входной набор данных.
        :param learning_rate: Скорость обучения.
        :param gradient: Градиент.
        :param weights: Список весов.
        :param i: Индекс первой координаты веса.
        :param j: Индекс второй координаты веса.
        """
        weights[i][j] -= learning_rate * gradient * input_dataset[j]

    @staticmethod
    def _calculate_learning_decay(epoch: int, epochs: int, learning_rate: float, learning_decay: float) -> float:
        """
        Вычисляет уменьшение скорости обучения (learning_rate) в зависимости от текущей эпохи.

        :param epoch: Текущая эпоха.
        :param epochs: Общее количество эпох.
        :param learning_rate: Текущая скорость обучения.
        :param learning_decay: Коэффициент уменьшения скорости обучения.
        :return: Обновленная скорость обучения.
        """
        if epoch % (epochs // 4) == 0 and epoch != 0:
            learning_rate *= learning_decay
        return learning_rate

    def update_weights(
            self, layer, gradient: float, lasso_regularization: bool,
            ridge_regularization: bool, learning_rate: float, regularization: float
    ) -> None:
        """
        Обновляет веса слоя с использованием заданных параметров Elastic Net регуляризации.

        :param layer: Объект слоя.
        :param gradient: Градиент.
        :param lasso_regularization: Использовать Lasso регуляризацию.
        :param ridge_regularization: Использовать Ridge регуляризацию.
        :param learning_rate: Скорость обучения.
        :param regularization: Параметр регуляризации.
        """
        for i in range(len(layer.weights)):
            for j in range(len(layer.weights[i])):
                regularization_term: float = 0.0
                if lasso_regularization:
                    regularization_term += self._get_lasso_regularization(regularization, layer.weights, i, j)
                if ridge_regularization:
                    regularization_term += self._get_ridge_regularization(regularization, layer.weights, i, j)
                self._calculate_gradient_descent(
                    layer.input_dataset, learning_rate, gradient + regularization_term, layer.weights, i, j
                )
                if not lasso_regularization and not ridge_regularization:
                    self._calculate_gradient_descent(
                        layer.input_dataset, learning_rate, gradient, layer.weights, i, j
                    )
        layer.bias -= learning_rate * gradient

    def __get_train_visualisation(self, epoch, prediction, target, layer):
        """
        Выводит визуализацию процесса обучения.

        :param epoch: Эпоха.
        :param prediction: Предсказанное значение.
        :param target: Целевое значение.
        :param layer: Объект слоя.
        """
        if epoch % 100 == 0:
            print(
                f'Epoch: {epoch}, error: {self._calculate_error(prediction, target):.1f}%, '
                f'prediction: {prediction * 10:.4f}, result: {sum(layer.get_layer_dataset()):.4f}'
            )

    def train(
            self, data_number: int, layer, epochs: int, learning_rate: float, learning_decay: float,
            error_tolerance: float, regularization: float, lasso_regularization: bool, ridge_regularization: bool
    ) -> tuple[list[list[float]], float]:
        """
        Обучает слой на основании данных.

        :param layer: Объект слоя.
        :param data_number: Номер данных.
        :param epochs: Количество эпох для обучения.
        :param learning_rate: Скорость обучения.
        :param learning_decay: Уменьшение скорости обучения.
        :param error_tolerance: Допустимый уровень ошибки.
        :param regularization: Параметр регуляризации.
        :param lasso_regularization: Использовать Lasso регуляризацию.
        :param ridge_regularization: Использовать Ridge регуляризацию.
        :return: Кортеж с обновленными весами и смещением (bias) слоя.
        """
        for epoch in range(epochs):
            layer.input_dataset = self.get_data_sample()
            prediction: float = sum(layer.get_layer_dataset())
            target: float = self.get_normalized_target_value(data_number)
            gradient: float = prediction - target
            self.update_weights(
                layer, gradient, lasso_regularization, ridge_regularization, learning_rate, regularization
            )
            self.__get_train_visualisation(epoch, prediction, target, layer)
            learning_rate = self._calculate_learning_decay(epoch, epochs, learning_rate, learning_decay)
            if abs(prediction - target) < error_tolerance:
                return layer.weights, layer.bias

    @staticmethod
    def __get_train_layers_on_dataset_visualisation(data_number, output_outer_layer):
        """
        Выводит визуальное представление результатов обучения для текущего набора данных.

        :param data_number: Номер данных.
        :param output_outer_layer: Выходной слой.
        """
        print(
            f'\nОбучение грани куба {data_number} завершено, результат: '
            f'{sum(output_outer_layer.get_layer_dataset()) * 10:.0f}\n'
        )

    def train_layers_on_dataset(
            self, data_number: int, hidden_layer_first, hidden_layer_second,
            output_outer_layer, epochs: int, learning_rate: float, learning_decay: float, error_tolerance: float,
            regularization: float, lasso_regularization: bool, ridge_regularization: bool
    ) -> None:
        """
        Обучает несколько слоев на наборе данных.

        :param data_number: Номер данных.
        :param hidden_layer_first: Первый скрытый слой.
        :param hidden_layer_second: Второй скрытый слой.
        :param output_outer_layer: Выходной слой.
        :param epochs: Количество эпох для обучения.
        :param learning_rate: Скорость обучения.
        :param learning_decay: Уменьшение скорости обучения.
        :param error_tolerance: Допустимый уровень ошибки.
        :param regularization: Параметр регуляризации.
        :param lasso_regularization: Использовать Lasso регуляризацию.
        :param ridge_regularization: Использовать Ridge регуляризацию.
        """
        weights: dict[str, list[list[float]]] = {}
        biases: dict[str, list[float]] = {}

        for i in range(len(self.dataset[self.data_name])):
            hidden_layer_first.input_dataset = self.get_data_sample()
            self.train(
                data_number, hidden_layer_first, epochs, learning_rate, learning_decay,
                error_tolerance, regularization, lasso_regularization, ridge_regularization
            )

            hidden_layer_second.input_dataset = hidden_layer_first.get_layer_dataset()
            self.train(
                data_number, hidden_layer_second, epochs, learning_rate, learning_decay,
                error_tolerance, regularization, lasso_regularization, ridge_regularization
            )

            output_outer_layer.input_dataset = hidden_layer_second.get_layer_dataset()
            self.train(
                data_number, output_outer_layer, epochs, learning_rate, learning_decay,
                error_tolerance, regularization, lasso_regularization, ridge_regularization
            )

            self.__get_train_layers_on_dataset_visualisation(data_number, output_outer_layer)
            data_number += 1

        weights['hidden_layer_first'] = hidden_layer_first.weights
        weights['hidden_layer_second'] = hidden_layer_second.weights
        weights['output_outer_layer'] = output_outer_layer.weights

        biases['hidden_layer_first'] = hidden_layer_first.bias
        biases['hidden_layer_second'] = hidden_layer_second.bias
        biases['output_outer_layer'] = output_outer_layer.bias

        self._save_weights_and_biases(weights, biases)
