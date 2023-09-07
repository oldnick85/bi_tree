import math
import logging
from typing import Any
from collections.abc import Iterable
from dataclasses import dataclass, field

logging.basicConfig(level=logging.DEBUG)

Position = list[float] | Iterable[float]

class Point:
    def __init__(self, coordinates : Position) -> None:
        self.__coordinates : list[float] = []
        if (type(coordinates) is list):
            self.__coordinates = coordinates.copy()
        else:
            for c in coordinates:
                self.__coordinates.append(c)
        return

    def __str__(self) -> str:
        return f"{self.__coordinates}"

    def __getitem__(self, key : int) -> float:
        return self.__coordinates[key]

    def dimension(self) -> int:
        return len(self.__coordinates)

    def middle(self, other : "Point") -> "Point":
        c = []
        assert len(self.__coordinates) == len(other.__coordinates)
        for i in range(len(self.__coordinates)):
            c.append((self.__coordinates[i] + other.__coordinates[i])/2)
        return Point(c)

    def distance2(self, other : "Point") -> float:
        d : float = 0.0
        assert len(self.__coordinates) == len(other.__coordinates)
        for i in range(len(self.__coordinates)):
            d += (self.__coordinates[i] - other.__coordinates[i])**2
        return d

    def distance(self, other : "Point") -> float:
        d : float = 0.0
        assert len(self.__coordinates) == len(other.__coordinates)
        for i in range(len(self.__coordinates)):
            d += (self.__coordinates[i] - other.__coordinates[i])**2
        return math.sqrt(d)

class Direction:
    def __init__(self, dir : int) -> None:
        self.__dir = dir
        return

    def __str__(self) -> str:
        return f"{self.__dir}"

    def hash(self) -> int:
        return self.__dir

    def get_nth(self, n : int) -> bool:
        return ((self.__dir & 2**n) != 0)

    def choose_coordinates(self, p1 : Point, p2 : Point) -> Point:
        assert p1.dimension() == p2.dimension()
        c = []
        for i in range(p1.dimension()):
            c.append(p2[i] if self.get_nth(i) else p1[i])
        return Point(c)

class Cuboid:
    def __init__(self, p1 : Point, p2 : Point) -> None:
        assert p1.dimension() == p2.dimension()
        c_min : list[float] = []
        c_mid : list[float] = []
        c_max : list[float] = []
        for i in range(p1.dimension()):
            c_min.append(min(p1[i], p2[i]))
            c_max.append(max(p1[i], p2[i]))
            c_mid.append((p1[i]+p2[i])/2)
        self.__p_min = Point(c_min)
        self.__p_mid = Point(c_mid)
        self.__p_max = Point(c_max)
        return

    def __str__(self) -> str:
        return f"({self.__p_min})-({self.__p_max})"

    def __repr__(self) -> str:
        return f"N[leaf={self.__leaf};{self.__contents_count};{len(self.__contents)};{self.__subnodes}]"

    def dimension(self) -> int:
        return self.__p_min.dimension()

    def point_min(self) -> Point:
        return self.__p_min

    def point_max(self) -> Point:
        return self.__p_max

    def point_direction(self, p : Point) -> Direction:
        d : int = 0
        n : int = 1
        for i in range(self.dimension()):
            assert p[i] < self.__p_max[i] and p[i] >= self.__p_min[i]
            if (p[i] >= self.__p_mid[i]):
                d += n
            n *= 2
        return Direction(d)

    def contains(self, p : Point) -> bool:
        assert self.__p_min.dimension() == p.dimension()
        for i in range(self.__p_min.dimension()):
            if (p[i] < self.__p_min[i]):
                return False
            if (p[i] >= self.__p_max[i]):
                return False
        return True

    def outside_radius(self, point : Point, radius : float) -> bool:
        """
        Гарантированное нахождение вне радиуса от точки
        ВНИМАНИЕ, отрицательный результат не гарантирует, что область есть внутри радиуса
        """
        for i in range(self.__p_min.dimension()):
            if (self.__p_min[i] > point[i]+radius):
                return True
            if (self.__p_max[i] < point[i]-radius):
                return True
        return False

    def intersect_radius(self, point : Point, radius : float) -> bool:
        """
        Гарантированное вхождение в окрестность точки
        ВНИМАНИЕ, отрицательный результат не гарантирует, что вся область содержится в окрестности
        """
        pass

    def max_distance_from_point(self, p : Point) -> float:
        """
        Наибольшее расстояние от точки
        """
        assert self.__p_min.dimension() == p.dimension()
        coordinates : list[float] = []
        for i in range(self.__p_min.dimension()):
            if (p[i] < self.__p_mid[i]):
                coordinates.append(self.__p_max[i])
            else:
                coordinates.append(self.__p_min[i])
        v = Point(coordinates)
        return v.distance(p)

class Path:
    def __init__(self, path : list[Direction]) -> None:
        self.__path = path
        return

class Content:
    def __init__(self, point : Point, data : Any = None) -> None:
        self.__point = point
        self.__data = data
        return

    def __str__(self) -> str:
        return f"{self.point()} {self.data()}"

    def __repr__(self) -> str:
        return f"{self.point()} {self.data()}"

    def point(self) -> Point:
        return self.__point

    def data(self) -> Any:
        return self.__data

@dataclass
class ClosestContent:
    max_distance : float = 0.0
    content : list[Content] = field(default_factory=list) 

class Node:
    def __init__(self, max_points_in_bucket : int, area : Cuboid, direction : Direction) -> None:
        self.__max_points_in_bucket : int = max_points_in_bucket
        self.__area : Cuboid = area
        self.__leaf : bool = True
        self.__subnodes : dict[int, "Node"] = {}
        self.__contents : list[Content] = []
        self.__contents_count : int = 0
        self.__direction = direction
        #logging.debug(f"NEW NODE {self.area()}")
        return

    def __str__(self) -> str:
        return f"N[leaf={self.__leaf};{self.__contents_count};{len(self.__contents)};dir={self.__direction};{self.__area}]"

    def __repr__(self) -> str:
        return f"N[leaf={self.__leaf};{self.__contents_count};{len(self.__contents)};{self.__subnodes}]"

    def area(self) -> Cuboid:
        return self.__area

    def get_areas(self) -> list[Cuboid]:
        areas : list[Cuboid] = [self.__area]
        for _, sn in self.__subnodes.items():
            areas.extend(sn.get_areas())
        return areas

    def get_contents(self) -> list[Content]:
        contents = self.__contents.copy()
        if (not self.__leaf):
            for _, sn in self.__subnodes.items():
                contents.extend(sn.get_contents())
        return contents

    def __add_subnode(self, direction : Direction) -> None:
        p_min = self.__area.point_min()
        p_max = self.__area.point_max()
        p_center = p_min.middle(p_max)
        p = direction.choose_coordinates(p_min, p_max)
        area = Cuboid(p, p_center)
        self.__subnodes[direction.hash()] = Node(self.__max_points_in_bucket, area, direction)
        return

    def add_content(self, content : Content) -> None:
        #logging.debug(f"add_content {content.point()} -> {self}")
        self.__contents_count += 1
        if (not self.__leaf):
            d = self.__area.point_direction(content.point()).hash()
            #logging.debug(f"direction={d}")
            if d not in self.__subnodes:
                self.__add_subnode(Direction(d))
            self.__subnodes[d].add_content(content)
        else:
            self.__contents.append(content)
            if (self.__contents_count > self.__max_points_in_bucket):
                #logging.debug("deepen")
                self.__leaf = False
                for c in self.__contents:
                    self.add_content(c)
                    self.__contents_count -= 1
                self.__contents = []
        return

    def del_content(self, content : Content) -> None:
        #logging.debug(f"del_content {content.point()} -> {self}")
        self.__contents_count -= 1
        if (not self.__leaf):
            d = self.__area.point_direction(content.point()).hash()
            #logging.debug(f"direction {d}")
            self.__subnodes[d].del_content(content)
            if (self.__contents_count <= self.__max_points_in_bucket):
                self.__contents = self.get_contents()
                self.__subnodes.clear()
                self.__leaf = True
        else:
            self.__contents = [c for c in self.__contents if c.data() != content.data()]
        return

    def move_content(self, content : Content, point : Position) -> None:
        """
        Изменить положение данных
        content - перемещаемые данные
        point - новое положение
        """
        #logging.debug(f"move_content {content.point()} {self} -> {point}")
        if (not self.__leaf):
            d_old = self.__area.point_direction(content.point()).hash()
            d_new = self.__area.point_direction(point).hash()
            #logging.debug(f"direction {d_old} -> {d_new}")
            if (d_new != d_old):
                self.__subnodes[d_old].del_content(content)
                if d_new not in self.__subnodes:
                    self.__add_subnode(Direction(d_new))
                self.__subnodes[d_new].add_content(Content(point, content.data()))
            else:
                self.__subnodes[d_new].move_content(content, point)
        else:
            self.__contents = [c for c in self.__contents if c.data() != content.data()]
            self.__contents.append(Content(point, content.data()))
        return

    def find_data_closest(self, point : Point, n : int, closest : ClosestContent) -> None:
        """
        Найти ближайшие данные
        point - точка
        n - количество ближайших
        c - найденные на предыдущих шагах ближайшие
        """
        logging.debug(f"find_data_closest {point} n={n} closest={closest} {self}")
        if (self.__leaf):
            for content in self.__contents:
                logging.debug(f"content={content}")
                if (len(closest.content) == 0) or (content.point().distance(point) < closest.max_distance):
                    if (len(closest.content) < n):
                        closest.content.append(content)
                    else:
                        closest.content[-1] = content
                    closest.content.sort(key=lambda c: c.point().distance(point))
                    closest.max_distance = closest.content[-1].point().distance(point)
            return
        else:
            d = None
            print(f"{closest.max_distance}")
            if (len(closest.content) == 0):
                d = self.__area.point_direction(point)
                subn = self.__subnodes.get(d)
                if (subn):
                    subn.find_data_closest(point, n, closest)
            for dr, subnode in self.__subnodes.items():
                if (dr == d):
                    continue
                if (len(closest.content) < n) or (not subnode.area().outside_radius(point, closest.max_distance)):
                    subnode.find_data_closest(point, n, closest)
        return

    def get_in_radius(self, point : Point, radius : float) -> list[Content]:
        """
        Найти все данные в круговой окрестности
        """
        #logging.debug(f"get_in_radius {point} r={radius} {self}")
        if self.__area.outside_radius(point, radius):
            return []
        in_radius : list[Content] = []
        if (not self.__leaf):
            for _, sn in self.__subnodes.items():
                in_radius.extend(sn.get_in_radius(point, radius))
        else:
            for c in self.__contents:
                if (c.point().distance(point) <= radius):
                    in_radius.append(c)
        return in_radius

class Tree:
    """
    Класс дерева для хранения пространственных данных
    """
    def __init__(self, dimension : int, p1 : Position, p2 : Position, max_points_in_bucket : int) -> None:
        """
        p1, p2 - точки, ограничивающие область хранения
        max_points_in_bucket - наибольшее количество точек, которое может храниться в листе дерева
        """
        self.__dimension = dimension
        p1 = Point(p1)
        p2 = Point(p2)
        assert p1.dimension() == self.__dimension
        assert p1.dimension() == p2.dimension()
        self.__root = Node(max_points_in_bucket, Cuboid(p1, p2), -1)
        self.__points = {}
        return

    def __str__(self) -> str:
        return f"2N_TREE dim={self.__dimension} root={self.__root}"

    def get_points(self) -> list[Point]:
        """
        Получить все координаты хранящихся в дереве данных
        """
        return list(self.__points.values())

    def find_data_closest(self, point : Position, n : int) -> list[Any]:
        """
        Найти несколько данных, наиболее близких к точке
        """
        assert n > 0
        if type(point) is not Point:
            point = Point(point)
        closest = ClosestContent()
        self.__root.find_data_closest(point, n, closest)
        return [c.data() for c in closest.content]

    def get_data_in_radius(self, point : Position, radius : float) -> list[Any]:
        """
        Найти все данные в круговой окрестности
        """
        if type(point) is not Point:
            point = Point(point)
        in_radius = self.__root.get_in_radius(point, radius)
        return [c.data() for c in in_radius]

    def _get_areas(self) -> list[Cuboid]:
        """
        Получить все окрестности, которые используются для построения дерева
        """
        return self.__root.get_areas()

    def add_content(self, point : Position, data : Any) -> None:
        """
        Добавить данные
        """
        #logging.debug(f"--------")
        if type(point) is not Point:
            point = Point(point)
        assert self.__root.area().contains(point)
        c = Content(point, data)
        self.__points[c.data()] = c.point()
        self.__root.add_content(c)
        return

    def del_data(self, data : Any) -> None:
        """
        Удалить данные
        """
        #logging.debug(f"--------")
        p = self.__points.pop(data)
        self.__root.del_content(Content(p, data))
        return

    def move_data(self, data : Any, point : Position) -> None:
        """
        Переместить данные
        """
        #logging.debug(f"--------")
        if type(point) is not Point:
            point = Point(point)
        p = self.__points.pop(data)
        self.__points[data] = point
        self.__root.move_content(Content(p, data), point)
        return

if __name__ == "__main__":
    t = Tree(2, [0.0, 0.0], [1.0, 1.0], 3)
    t.add_content([0.7, 0.7], "A")
    t.add_content([0.75, 0.75], "AA")
    t.add_content([0.3, 0.7], "B")
    t.add_content([0.3, 0.3], "C")
    t.add_content([0.7, 0.3], "D")
    closest = t.find_data_closest([0.31, 0.31], 3)
    print(closest)
    print(f"{t}")
    t.del_data("A")
    print(f"{t}")
    t.del_data("AA")
    t.del_data("B")
    print(f"{t}")