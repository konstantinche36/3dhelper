from typing import Generic, TypeVar, List
from XPoint import XPoint

# Определяем типовую переменную для параметризации
T = TypeVar('T', bound=XPoint)

class XFigure(Generic[T]):
    def __init__(self, name: str):
        self.name = name
        self.points: List[T] = []

    def add_point(self, point: T) -> None:
        self.points.append(point)

    def edit_point(self, old_point: T, new_point: T) -> None:
        try:
            index = self.points.index(old_point)
            self.points[index] = new_point
        except ValueError:
            print("Точка для редактирования не найдена")

    def delete_point(self, point: T) -> None:
        try:
            self.points.remove(point)
        except ValueError:
            print("Точка для удаления не найдена")
