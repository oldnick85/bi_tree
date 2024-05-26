from tkinter import Tk, Canvas
import random
import time
from dataclasses import dataclass

import os
import sys
project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_directory)
from src.bi_tree import Tree

AREA_WIDTH = 600.0
AREA_HEIGTH = 600.0
POINTS_COUNT=1000

@dataclass
class GuiPoint:
    x : float
    y : float
    vx : float
    vy : float

    def velocity_step(self) -> None:
        p = self
        p.x += p.vx
        if p.x < 0.0:
            p.vx = -p.vx
            p.x = 0.0
        if p.x >= AREA_WIDTH:
            p.vx = -p.vx
            p.x = AREA_WIDTH-1
        p.y += p.vy
        if p.y < 0.0:
            p.vy = -p.vy
            p.y = 0.0
        if p.y >= AREA_HEIGTH:
            p.vy = -p.vy
            p.y = AREA_HEIGTH-1
        return

class GuiTk:
    def __init__(self) -> None:
        self.__root = Tk()
        self.__root.title("")
        self.__root.geometry(f"{int(AREA_WIDTH)}x{int(AREA_HEIGTH)}")
        self.__canvas = Canvas(bg="white", width=int(AREA_WIDTH), height=int(AREA_HEIGTH))
        self.__canvas.place(x=0, y=0)
        self.__canvas.bind('<Motion>', self.canvas_mouse_move)
        self.__canvas.bind("<Button-1>", self.canvas_mouse_click)
        self.__graph = Tree(2, [0.0, 0.0], [AREA_WIDTH, AREA_HEIGTH], 2)
        self.__graph.add_content([AREA_WIDTH/2, AREA_HEIGTH/2], "cursor")
        self.__points : list[GuiPoint] = []
        self.__points_added = False
        for _ in range(POINTS_COUNT):
            self.__points.append(GuiPoint(x=random.uniform(0.0, AREA_WIDTH), \
                                          y=random.uniform(0.0, AREA_HEIGTH), \
                                          vx=random.uniform(-1.0, 1.0), \
                                          vy=random.uniform(-1.0, 1.0)))
        self.__in_radius : list[int] = []
        self.__in_radius_center = [AREA_WIDTH/2, AREA_HEIGTH/2]
        self.__in_radius_radius = 25
        return

    def update_clock(self) -> None:
        tm_start = time.time()
        self.update()
        tm_mid = time.time()
        self.draw()
        tm_end = time.time()
        self.__root.after(10, self.update_clock)
        self.__root.title(f"update {tm_mid - tm_start:.3f}; show {tm_end - tm_mid:.3f}")
        return

    def update(self) -> None:
        if not self.__points_added:
            for i, p in enumerate(self.__points):
                self.__graph.add_content([p.x, p.y], i)
            self.__points_added = True
        else:
            for i, p in enumerate(self.__points):
                p.velocity_step()
                self.__graph.move_data(i, [p.x, p.y])
            self.__in_radius = self.__graph.get_data_in_radius( self.__in_radius_center, self.__in_radius_radius)
        return

    def draw(self) -> None:
        self.__canvas.delete("all")
        areas = self.__graph._get_areas()
        for area in areas:
            self.__canvas.create_rectangle(area.point_min()[0]+1, area.point_min()[1]+1, area.point_max()[0], area.point_max()[1], outline='grey')

        self.__canvas.create_oval(self.__in_radius_center[0]-self.__in_radius_radius, \
                                  self.__in_radius_center[1]-self.__in_radius_radius, \
                                  self.__in_radius_center[0]+self.__in_radius_radius, \
                                  self.__in_radius_center[1]+self.__in_radius_radius)

        for i, p in enumerate(self.__points):
            c = "red" if (i in self.__in_radius) else "green"
            self.__canvas.create_oval(p.x-1, p.y-1, p.x+1, p.y+1, fill=c, outline=c)
        return

    def canvas_mouse_move(self, event) -> None:
        try:
            x = event.x
            y = event.y
            self.__in_radius_center = [x, y]
        except Exception as e:
            self.__root.destroy()
            raise e
        return

    def canvas_mouse_click(self, event) -> None:
        print("clicked at", event.x, event.y)
        return
 
    def run(self) -> None:
        self.update_clock()
        self.__root.mainloop()
        return

if __name__ == "__main__":
    gui = GuiTk()
    gui.run()