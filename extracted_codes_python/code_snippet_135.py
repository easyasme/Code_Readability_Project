from manimlib import *
import numpy as np
import subprocess
import random
import json


class Utils:
    @staticmethod
    def create_table_with_removable_objects(
            data: list[list] or dict,
            removable_keys: list[str],
            fontsize: int = 28,
            x_buff: float = 0.3,
            y_buff: float = 0.5,
            header_row_present: bool = True,
            scale: float = 1,
    ):
        amount_of_columns = len(list(data.values())[0]) + 1
        amount_of_rows = len(data)
        max_x = 0
        max_y = 0
        shift_dict = {}
        for i in range(amount_of_columns):
            for j in range(amount_of_rows):
                if i == 0:
                    value = list(data.keys())[j]
                else:
                    value = str(list(data.values())[j][i - 1])
                max_x = max(max_x, Text(value, font_size=fontsize).get_width())
                max_y = max(max_y, Text(value, font_size=fontsize).get_height())
        x_size = max_x + x_buff
        y_size = max_y + y_buff
        table = VGroup()
        removeable_objects = VGroup()
        align = LEFT
        for i in range(amount_of_columns):
            column = VGroup()
            to_remove_counter = 0
            for j in range(amount_of_rows):
                if i == 0:
                    value = list(data.keys())[j]
                else:
                    value = str(list(data.values())[j][i - 1])
                text = Text(value, alignment="center", font_size=fontsize)
                cell_bg = Rectangle(width=x_size, height=y_size,
                                    fill_color=WHITE, fill_opacity=0.0, stroke_width=1)
                text.move_to(cell_bg.get_center())
                cell = VGroup(cell_bg, text)
                column.add(cell)
                if list(data.keys())[j] in removable_keys:
                    removeable_objects.add(cell)
                    to_remove_counter += 1
                else:
                    str_i_j = str(i) + str(j)
                    shift_dict[str_i_j] = (cell, i, j, to_remove_counter * y_size)

            column.arrange(DOWN, buff=0, aligned_edge=align)
            table.add(column)
        table.arrange(RIGHT, buff=0)
        table.move_to(ORIGIN)
        table.scale(scale)

        return table, removeable_objects, shift_dict

    @staticmethod
    def get_text_to_indicate(text_to_find, reaction_table, text_to_indicate):
        for obj in reaction_table:
            if isinstance(obj, VGroup):
                Utils.get_text_to_indicate(text_to_find, obj, text_to_indicate)
            elif isinstance(obj, Text):
                if obj.get_text() in text_to_find:
                    text_to_indicate.append(obj)

        return text_to_indicate

    @staticmethod
    def create_metabolic_network(
            nodes_dict: dict,
            edges_dict: dict,
            circle_settings: dict = None,
            line_settings: dict = None,
            arrow_settings: dict = None,
            scale: float = 1,
            expression_settings: dict = None,
            paths: list = None,
            node_paths: list = None
    ):
        circle_settings_default = {
            "radius": 0.2,
            "color": WHITE,
            "fill_color": BLUE,
            "fill_opacity": 1.0,
            "stroke_width": 1.5,
        }
        line_settings_default = {
            "width": 6,
            "color": WHITE,
            "fill_opacity": 0.8,
        }
        arrow_settings_default = {
            "stroke_width": 1.5,
            "color": WHITE,
            "fill_color": BLUE,
        }
        expression_settings_default = {
            "show_edge_expression": True,
            "font size": 22,
            "color": WHITE,
            "distance from line": 0.3,
        }

        if circle_settings is None:
            circle_settings = circle_settings_default
        circle_radius = circle_settings.get("radius", circle_settings_default["radius"])
        circle_color = circle_settings.get("color", circle_settings_default["color"])
        circle_fill_color = circle_settings.get("fill_color", circle_settings_default["fill_color"])
        circle_fill_opacity = circle_settings.get("fill_opacity", circle_settings_default["fill_opacity"])
        circle_stroke_width = circle_settings.get("stroke_width", circle_settings_default["stroke_width"])

        if line_settings is None:
            line_settings = line_settings_default
        edge_width = line_settings.get("width", line_settings_default["width"])
        edge_color = line_settings.get("color", line_settings_default["color"])
        edge_fill_opacity = line_settings.get("fill_opacity", line_settings_default["fill_opacity"])

        if arrow_settings is None:
            arrow_settings = arrow_settings_default
        arrow_color = arrow_settings.get("color", arrow_settings_default["color"])
        arrow_stroke_width = arrow_settings.get("stroke_width", arrow_settings_default["stroke_width"])

        if expression_settings is None:
            expression_settings = expression_settings_default
        show_edge_expression = expression_settings.get("show_edge_expression", expression_settings_default["show_edge_expression"])
        font_size = expression_settings.get("font size", expression_settings_default["font size"])
        color = expression_settings.get("color", expression_settings_default["color"])
        distance_from_line = expression_settings.get("distance from line", expression_settings_default["distance from line"])

        show_path_to_highlight = True if paths is not None else False
        show_node_paths = True if node_paths is not None else False
        paths = node_paths if show_node_paths else paths
        nodes = {}
        edges = {}
        if paths is not None:
            highlighted_edges = [[] for path in paths]
        arrows = []

        for node, position in nodes_dict.items():
            circle = Circle(
                radius=circle_radius,
                stroke_color=circle_color,
                fill_color=circle_fill_color,
                fill_opacity=circle_fill_opacity,
                stroke_width=circle_stroke_width,
            )
            circle.move_to(position)
            nodes[node] = circle
            if show_path_to_highlight:
                for idx, path in enumerate(paths):
                    if any(node in path_vars for path_vars in path) and (
                            node not in highlighted_edges[idx]
                    ):
                        highlighted_edges[idx].append(circle)
            if show_node_paths:
                for idx, path in enumerate(node_paths):
                    if node in path and node not in highlighted_edges[idx]:
                        highlighted_edges[idx].append(circle)
        x_middle = [node.get_center()[0] for node in nodes.values()]
        y_middle = [node.get_center()[1] for node in nodes.values()]
        middle_of_nodes = np.array([np.mean(x_middle), np.mean(y_middle), 0])
        print(len(edges_dict))

        for edge, list in edges_dict.items():
            expression = list[1] if len(list) > 1 else None
            start = list[0][0]
            end = list[0][1]
            if start == "":
                arrow = Arrow(nodes.get(end).get_left() + LEFT * 0.9,
                              nodes.get(end).get_center() + RIGHT * 0.05)
                arrow.set_stroke(
                    color=arrow_color,
                    width=arrow_stroke_width
                )
                arrows.append(arrow)
            elif end == "":
                arrow = Arrow(nodes.get(start).get_center() + LEFT * 0.05,
                              nodes.get(start).get_right() + RIGHT * 0.9)
                arrow.set_stroke(
                    color=arrow_color,
                    width=arrow_stroke_width
                )
                arrows.append(arrow)
            else:
                full_line = Line(nodes[start].get_center(),
                                 nodes[end].get_center())
                vector = full_line.get_unit_vector()
                start_node_radius = nodes[start].get_radius()
                end_node_radius = nodes[end].get_radius()

                new_line = Line(
                    nodes[start].get_center() + vector * start_node_radius,
                    nodes[end].get_center() - vector * end_node_radius
                )
                new_line.set_stroke(
                    color=edge_color,
                    width=edge_width
                )
                edges[edge] = new_line
                if show_edge_expression:
                    if expression is not None:
                        expression_text = Text(
                            str(expression),
                            font_size=font_size,
                            color=color
                        )
                        tangential_vector = np.array([new_line.get_unit_vector()[1], - new_line.get_unit_vector()[0], 0])
                        if np.dot(tangential_vector, middle_of_nodes - new_line.get_center()) > 0:
                            tangential_vector = -tangential_vector
                        if any([abs(value) >= 0.9 and abs(value) <= 1.1 for value in tangential_vector]):
                            distance_to_use = distance_from_line * 1.5
                        else:
                            distance_to_use = distance_from_line
                        expression_text.next_to(new_line.get_center(),
                                                tangential_vector,
                                                buff=distance_to_use,
                                                aligned_edge=ORIGIN)

                        edges[edge + "_text"] = expression_text

                if show_path_to_highlight:
                    for idx, path in enumerate(paths):
                        if edge in path:
                            highlighted_edges[idx].append(new_line)
                if show_node_paths:
                    for idx, path in enumerate(node_paths):
                        if start in path and end in path:
                            highlighted_edges[idx].append(new_line)

        full_object = VGroup(*nodes.values(), *edges.values(), *arrows).scale(scale)
        return (
            VGroup(*nodes.values(), *edges.values()),
            nodes,
            edges,
            highlighted_edges,
            arrows,
            full_object
        )

    @staticmethod
    def create_connected_network(nodes_dict, through_node_1, through_node_2):
        for node, position in nodes_dict.items():
            position.append(0)

        probability_function = lambda x: 1 / (1 + np.exp(-0.5 * (x - 2.5)))
        edges_dict = {}
        total_edges = 0

        for idx, (node, value) in enumerate(nodes_dict.items()):
            for node_2, value_2 in list(nodes_dict.items())[idx:]:
                if node.startswith("IN") and node_2.startswith("A"):
                    edges_dict[f"{node}>{node_2}"] = [(node, node_2)]
                    total_edges += 1
                    continue
                elif node.startswith("N") and node_2.startswith("OUT"):
                    edges_dict[f"{node}>{node_2}"] = [(node, node_2)]
                    total_edges += 1
                    continue

                x_1 = value[0]
                y_1 = value[1]
                x_2 = value_2[0]
                if x_2 == x_1:
                    continue
                y_2 = value_2[1]
                distance = np.sqrt(((x_1 - x_2) * 2) ** 2 + ((y_1 - y_2)) ** 2)
                probability = probability_function(distance)
                # print(f"{node}>{node_2}, Distance: {distance}, Probability: {probability}")
                if np.random.rand() > probability:
                    edges_dict[f"{node}>{node_2}"] = [(node, node_2)]
                    total_edges += 1
                    # print(f"{node}>{node_2}")

        def find_paths(graph, start_node, end_node, path=None):
            if path is None:
                path = []
            path = path + [start_node]
            if start_node == end_node:
                return [path]
            if start_node not in graph:
                return []
            paths = []
            for neighbor in graph[start_node]:
                if neighbor not in path:  # Avoid revisiting nodes
                    new_paths = find_paths(graph, neighbor, end_node, path)
                    paths.extend(new_paths)

            return paths

        graph = {}
        for list_ in edges_dict.values():
            u, v = list_[0]
            if u not in graph:
                graph[u] = []
            graph[u].append(v)

        IN_nodes = [node for node in nodes_dict.keys() if node.startswith("IN")]
        OUT_nodes = [node for node in nodes_dict.keys() if node.startswith("OUT")]
        total_paths = []
        for IN_node in IN_nodes:
            for OUT_node in OUT_nodes:
                paths = find_paths(graph, IN_node, OUT_node)
                paths = [path[:-1] for path in paths]  #remove last element
                paths = [path[1:] for path in paths]  #remove first element
                if len(total_paths) == 0:
                    total_paths = paths
                else:
                    # if a path in total paths not in current path, remove
                    new_total_paths = []
                    for path in total_paths:
                        if path in paths:
                            new_total_paths.append(path)
                    total_paths = new_total_paths
                print(f'IN: {IN_node}, OUT: {OUT_node}, len: {len(total_paths)}')
        paths_through_J1 = [path for path in total_paths if f"{through_node_1}" in path]
        paths_through_E4 = [path for path in total_paths if f"{through_node_2}" in path]

        random_paths_J1 = random.sample(paths_through_J1, 15)
        random_paths_E4 = random.sample(paths_through_E4, 15)
        random_paths_J1 = [IN_nodes + path + OUT_nodes for path in random_paths_J1]
        random_paths_E4 = [IN_nodes + path + OUT_nodes for path in random_paths_E4]
        node_paths = random_paths_J1 + random_paths_E4

        ## function that increases stepsize from initial_runtime to last_runtime in 200 steps

        nodes_in_paths = []
        for path in node_paths:
            unique_nodes = list(set(path))
            nodes_in_paths.extend(unique_nodes)
            nodes_in_paths = list(set(nodes_in_paths))
        nodes_not_in_paths = [node for node in nodes_dict.keys() if node not in nodes_in_paths]

        new_edges_dict = {}
        for key, list_ in edges_dict.items():
            u, v = list_[0]
            if u in nodes_not_in_paths or v in nodes_not_in_paths:
                continue
            new_edges_dict[key] = [(u, v)]

        for idx, (node, value) in enumerate(nodes_dict.items()):
            if node.startswith("IN"):
                new_edges_dict[f">{node}"] = [("", node)]
            elif node.startswith("OUT"):
                new_edges_dict[f"{node}>"] = [(node, "")]
        new_nodes_dict = {}
        for node, value in nodes_dict.items():
            if node in nodes_not_in_paths:
                continue
            new_nodes_dict[node] = value
        print(new_nodes_dict)
        return (
            new_nodes_dict,
            new_edges_dict,
            node_paths,
            random_paths_J1,
            random_paths_E4
        )


class Main(InteractiveScene):

    def intro(self):
        ### start intro
        text_macsbio = Text(
            "MaCSBio",
        ).scale(1)
        # text_macsbio.to_edge(UP)
        self.play(Write(text_macsbio),
                  run_time=3 * self.speed)
        text_route_optimization = Text(
            "Route Optimizations",
        ).scale(1)
        text_route_optimization.next_to(text_macsbio, DOWN)
        self.play(Write(text_route_optimization),
                  run_time=3 * self.speed)
        self.wait(1 * self.speed)
        self.play(FadeOut(text_macsbio),
                  FadeOut(text_route_optimization),
                  run_time=1 * self.speed)

    def does_gene_expression_predict_metabolic_activity(self):
        specific_question_text_1 = Text(
            "Does gene expression predict metabolic activity",
        ).scale(0.6)
        question_mark = Text("?").scale(2)
        group = VGroup(specific_question_text_1, question_mark).arrange(RIGHT)
        box = SurroundingRectangle(group, color=BLUE)
        vgroup = VGroup(group, box).shift(UP * 2)
        self.play(Write(group),
                  Write(box, run_time=1 * self.speed),
                  run_time=2 * self.speed)
        self.wait(0.5 * self.speed)
        specific_question_text_1_2 = Text(
            "Does gene expression predict \n metabolic activity",
            alignment="center"
        ).scale(0.5)
        question_mark = Text("?").scale(1.5)
        group = VGroup(specific_question_text_1_2, question_mark).arrange(RIGHT)
        box = SurroundingRectangle(group, color=BLUE)
        vgroup2 = VGroup(group, box).shift(LEFT * 4).shift(UP)
        self.vom_dict["vgroup2"] = vgroup2
        self.play(ReplacementTransform(vgroup, vgroup2),
                  run_time=1 * self.speed)
        gene_expression = {
            "Gene": ["Expression"],
            "ACTN1": [0.5],
            "ACTN2": [22.3],
            "GAPDH": [30.9],
            "PFK": [9.5],
            "ENO": [1.2],
            "HDAC1": [2.7],
            "METTL16": [203.2],
            "MDH1": [592.0],
            "CS": [93.0],
        }
        removable_keys = ["ACTN1", "ACTN2", "HDAC1", "METTL16"]
        (table, removable_objects, shift_dict
         ) = Utils.create_table_with_removable_objects(
            data=gene_expression,
            removable_keys=removable_keys,
            fontsize=12,
            x_buff=0.1,
            y_buff=0.3,
            header_row_present=True,
            scale=1,
        )
        table.next_to(vgroup2, DOWN, aligned_edge=LEFT)
        self.play(FadeIn(table),
                  run_time=1 * self.speed
                  )
        remove_non_metabolic_genes_text = Text(
            "Remove non-metabolic genes",
            font_size=18,
            color=WHITE
        ).scale(1).next_to(table, RIGHT, aligned_edge=UP)
        self.play(FadeIn(remove_non_metabolic_genes_text),
                  run_time=1 * self.speed)
        self.play(
            removable_objects.animate.shift(RIGHT * 2),
            run_time=(0.5) * self.speed
        )
        removable_objects_copy = removable_objects.copy()
        removable_objects_copy.shift(UP * 2).set_opacity(0.0)

        self.play(
            Transform(removable_objects, removable_objects_copy),
            run_time=(0.5) * self.speed
        )
        self.play(
            *[shift[0].animate.shift(UP * shift[3]) for shift in shift_dict.values()],
            FadeOut(remove_non_metabolic_genes_text),
            run_time=(0.5) * self.speed
        )
        self.wait((0.5) * self.speed)
        GPR_text_and_arrow = VGroup(
            Text("GPR"),
            Arrow(ORIGIN, RIGHT)
        ).arrange(DOWN)
        GPR_text_and_arrow.next_to(table, RIGHT, aligned_edge=UP)
        self.play(Write(GPR_text_and_arrow),
                  run_time=1 * self.speed)
        self.wait((0.5) * self.speed)
        reaction_table = {
            "Reaction": ["Expression"],
            "MAR04373": [30.9],
            "MAR04379": [9.5],
            "MAR04363": [1.2],
            "MAR04139": [592.0],
            "MAR04145": [93.0],
        }
        (reaction_table, reaction_table_removable_objects, reaction_table_shift_dict
         ) = Utils.create_table_with_removable_objects(
            data=reaction_table,
            removable_keys=[],
            fontsize=12,
            x_buff=0.1,
            y_buff=0.3,
            header_row_present=True,
            scale=1,
        )
        reaction_table.next_to(GPR_text_and_arrow, RIGHT, aligned_edge=UP)
        self.play(FadeIn(reaction_table),
                  run_time=1 * self.speed)
        self.play(
            FadeOut(table),
            run_time=1 * self.speed
        )
        self.play(
            VGroup(reaction_table,
                   GPR_text_and_arrow).animate.next_to(vgroup2, DOWN, aligned_edge=LEFT),
            run_time=1 * self.speed
        )
        self.play(
            LaggedStart(
                FadeOut(GPR_text_and_arrow),
                reaction_table.animate.next_to(vgroup2, DOWN, aligned_edge=LEFT),
                run_time=1 * self.speed,
                lag_ratio=0.5
            ))
        nodes_dict = {
            "A": [0, 1, 0],
            "B": [1, 2, 0],
            "C": [2, 2, 0],
            "D": [1.5, 0, 0],
            "E": [3, 1, 0],
        }
        edges_dict = {
            ">A": [("", "A")],
            "AB": [("A", "B"), 30.9],
            "BC": [("B", "C"), 592.0],
            "CE": [("C", "E"), 93.0],
            "AD": [("A", "D"), 9.5],
            "DE": [("D", "E"), 1.2],
            "E>": [("E", "")],
        }
        paths = [
            ["AB", "BC", "CE"],
            ["AD", "DE"],
        ]
        (
            metabolic_network,
            nodes,
            edges,
            highlighted_edges,
            arrows_to_grow,
            full_object
        ) = Utils.create_metabolic_network(
            nodes_dict=nodes_dict,
            edges_dict=edges_dict,
            circle_settings=None,
            line_settings=None,
            scale=0.6,
            expression_settings=None,
            paths=paths
        )
        full_object.next_to(reaction_table, RIGHT * 0.25)
        self.play(FadeIn(metabolic_network),
                  run_time=1 * self.speed)
        self.play(
            GrowArrow(arrows_to_grow[0]),
            run_time=1 * self.speed
        )
        self.play(
            GrowArrow(arrows_to_grow[1]),
            run_time=1 * self.speed
        )
        text_to_indicate = []
        text_to_find = ["MAR04373", "MAR04139", "MAR04145", "30.9", "592.0", "93.0"]
        text_to_indicate = Utils.get_text_to_indicate(
            text_to_find=text_to_find,
            reaction_table=reaction_table,
            text_to_indicate=text_to_indicate
        )
        self.play(
            *[Indicate(line) for line in highlighted_edges[0]],
            *[Indicate(text) for text in text_to_indicate],
            run_time=2 * self.speed
        )
        text_to_indicate = []
        text_to_find = ["MAR04379", "MAR04363", "9.5", "1.2"]
        text_to_indicate = Utils.get_text_to_indicate(
            text_to_find=text_to_find,
            reaction_table=reaction_table,
            text_to_indicate=text_to_indicate
        )
        self.play(
            *[Indicate(line) for line in highlighted_edges[1]],
            *[Indicate(text) for text in text_to_indicate],
            run_time=2 * self.speed
        )
        full_subscene = VGroup(vgroup2,
                               reaction_table,
                               full_object)
        box = SurroundingRectangle(full_subscene, color=BLUE)
        self.play(Write(box),
                  run_time=1 * self.speed)
        self.vom_dict["reaction_table"] = reaction_table
        self.vom_dict["metabolic_network"] = metabolic_network
        self.vom_dict["full_object"] = full_object
        self.vom_dict["box_question_1"] = box

    def create_sample_clustering_graph(self):
        #### create clustering tsne
        vgroup = self.vom_dict["prediction_question"]
        height_box = self.vom_dict["box_question_1"].get_height()
        height_vgroup = vgroup.get_height()
        height_new_box = height_box - height_vgroup - 1.2
        self.vom_dict["height_new_box"] = height_new_box
        sample_clustering_text = Text(
            "Sample Clustering\n"
            "(e.g. t-SNE)",
            font_size=20,
            opacity=0.8
        ).scale(1)
        sample_clustering_text.next_to(vgroup, DOWN, aligned_edge=LEFT)
        num_points = 20
        rect = Rectangle(width=vgroup.get_width() / 2, height=height_new_box, color=BLUE)
        self.vom_dict["cluster_rect"] = rect
        rect.next_to(sample_clustering_text, DOWN, aligned_edge=LEFT)
        sample_clustering_text.next_to(rect, UP, aligned_edge=ORIGIN)
        rect_center = rect.get_center() - np.array([rect.get_width() / 4, rect.get_height() / 6, 0])
        points_2d_normal_distribution = np.random.normal(loc=(rect_center[0], rect_center[1]), scale=0.2, size=(num_points, 2))

        new_center = rect.get_center() + np.array([rect.get_width() / 9, -rect.get_height() / 10, 0])
        new_points = np.random.normal(loc=(new_center[0], new_center[1]), scale=0.2, size=(num_points, 2))
        self.play(ShowCreation(rect),
                  FadeIn(sample_clustering_text),
                  run_time=1 * self.speed)
        self.wait(0.5 * self.speed)
        dots = [Dot((point[0], point[1], 0), radius=0.05,
                    fill_color=PURPLE) for point in points_2d_normal_distribution]

        legend_dot_1 = Dot(radius=0.05, fill_color=PURPLE)
        legend_dot_2 = Dot(radius=0.05, fill_color=ORANGE)
        legend_text_1 = Text("Cluster 1", color=PURPLE, font_size=18).scale(1)
        legend_text_2 = Text("Cluster 2", color=ORANGE, font_size=18).scale(1)
        legend_1 = VGroup(legend_dot_1, legend_text_1).arrange(RIGHT, buff=0.09)
        legend_2 = VGroup(legend_dot_2, legend_text_2).arrange(RIGHT, buff=0.09)
        legend = VGroup(legend_1, legend_2).arrange(DOWN)
        legend.next_to(rect.get_right(), LEFT, aligned_edge=RIGHT).shift(UP * 0.5).shift(RIGHT * 0.15)
        self.play(FadeIn(dots[0]),
                  run_time=0.1 * self.speed)
        self.play(Write(legend),
                  run_time=0.1 * self.speed)
        [self.play(FadeIn(dot), run_time=(0.1) * self.speed) for dot in dots[1:]]
        self.wait(0.5 * self.speed)
        dots_new = [Dot((point[0], point[1], 0), radius=0.05,
                        color=ORANGE, fill_color=ORANGE) for
                    point in new_points]
        [self.play(FadeIn(dot), run_time=(0.2) * self.speed) for dot in dots_new]
        clustering_graph = VGroup(legend, rect, sample_clustering_text, *dots, *dots_new)
        self.vom_dict["clustering_graph"] = clustering_graph

    def create_network_graph_subscene(self):
        specific_question_text_2 = Text(
            "Can we cluster using metabolic predictions \n"
            "better than using just gene expression?",
            opacity=0.8
        ).scale(0.5)
        question_mark = Text("?").scale(1.5)
        group = VGroup(specific_question_text_2, question_mark).arrange(RIGHT)
        box = SurroundingRectangle(group, color=BLUE)
        vgroup = VGroup(group, box)
        vgroup.next_to(self.vom_dict["vgroup2"], RIGHT * 2)
        self.vom_dict["prediction_question"] = vgroup
        self.play(Write(group),
                  Write(box, run_time=1 * self.speed),
                  run_time=2 * self.speed)
        self.wait(0.5 * self.speed)

        vgroup_3 = self.vom_dict["prediction_question"]
        height_box = self.vom_dict["box_question_1"].get_height()
        height_vgroup = vgroup_3.get_height()
        height_new_box = height_box - height_vgroup - 1.2
        self.create_sample_clustering_graph()

        ####
        chararacteristics_text = Text(
            "Do these clusters share\n"
            "metabolic characteristics?",
            opacity=0.8,
            font_size=20
        ).scale(1)
        chararacteristics_text.next_to(vgroup, DOWN, aligned_edge=RIGHT)
        char_rect = Rectangle(width=vgroup.get_width() / 2, height=height_new_box, color=BLUE)
        char_rect.next_to(chararacteristics_text, DOWN, aligned_edge=LEFT)
        chararacteristics_text.next_to(char_rect, UP, aligned_edge=ORIGIN)
        char_rect.next_to(self.vom_dict["cluster_rect"], RIGHT, aligned_edge=UP, buff=0.1)
        self.play(ShowCreation(char_rect),
                  FadeIn(chararacteristics_text),
                  run_time=1 * self.speed)

        ### more complicated toy network with different opacity or colours for things being chosen more or less (linetrace
        ### network_on_grid
        nodes_dict = {
            "IN1": [0, 2],
            "IN2": [0, 4],
            "IN3": [0, 8],
            "A1": [1, 1],
            "A2": [1, 3],
            "A3": [1, 4],
            "A4": [1, 6],
            "A5": [1, 7],
            "A6": [1, 8],
            "B1": [2, 2],
            "B2": [2, 3],
            "B3": [2, 4],
            "B4": [2, 5],
            "B5": [2, 7],
            "B6": [2, 8],
            "B7": [2, 9],
            "C1": [3, 2],
            "C2": [3, 7],
            "C3": [3, 9],
            "D1": [4, 1],
            "D2": [4, 2],
            "D3": [4, 3],
            "D4": [4, 8],
            "E1": [5, 1],
            "E2": [5, 3],
            "E3": [5, 4],
            "E4": [5, 5],
            "F1": [6, 4],
            "F2": [6, 8],
            "F3": [6, 9],
            "G1": [7, 4],
            "G2": [7, 5],
            "G3": [7, 7],
            "H1": [8, 2],
            "H2": [8, 8],
            "H3": [8, 9],
            "I1": [9, 1],
            "I2": [9, 2],
            "I3": [9, 3],
            "I4": [9, 4],
            "I5": [9, 7],
            "I6": [9, 8],
            "I7": [9, 9],
            "J1": [10, 2],
            "J2": [10, 3],
            "J3": [10, 6],
            "J4": [10, 8],
            "K1": [11, 2],
            "K2": [11, 4],
            "K3": [11, 8],
            "K4": [11, 9],
            "L1": [12, 1],
            "L2": [12, 3],
            "L3": [12, 4],
            "L4": [12, 7],
            "M1": [13, 2],
            "M2": [13, 7],
            "M3": [13, 9],
            "N1": [14, 1],
            "N2": [14, 4],
            "N3": [14, 6],
            "N4": [14, 8],
            "OUT1": [15, 1],
            "OUT2": [15, 3],
            "OUT3": [15, 5],
            "OUT4": [15, 8],
        }

        json_file_name = {
            "edges": "data/edges_dict.json",
            "nodes": "data/nodes_dict.json",
            "node_paths": "data/node_paths.json",
            "random_paths_J1": "data/random_paths_J1.json",
            "random_paths_E4": "data/random_paths_E4.json"
        }
        if any([not os.path.exists(file) for file in json_file_name.values()]):
            (new_nodes_dict,
             new_edges_dict,
             node_paths,
             random_paths_J1,
             random_paths_E4
             ) = Utils.create_connected_network(nodes_dict, "J1", "E4")
            with open(json_file_name["edges"], "w") as f:
                json.dump(new_edges_dict, f)
            with open(json_file_name["nodes"], "w") as f:
                json.dump(new_nodes_dict, f)
            with open(json_file_name["node_paths"], "w") as f:
                json.dump(node_paths, f)
            with open(json_file_name["random_paths_J1"], "w") as f:
                json.dump(random_paths_J1, f)
            with open(json_file_name["random_paths_E4"], "w") as f:
                json.dump(random_paths_E4, f)
        else:
            with open(json_file_name["edges"], "r") as f:
                new_edges_dict = json.load(f)
            with open(json_file_name["nodes"], "r") as f:
                new_nodes_dict = json.load(f)
            with open(json_file_name["node_paths"], "r") as f:
                node_paths = json.load(f)
            with open(json_file_name["random_paths_J1"], "r") as f:
                random_paths_J1 = json.load(f)
            with open(json_file_name["random_paths_E4"], "r") as f:
                random_paths_E4 = json.load(f)

        sample_N = 200
        initial_runtime = 0.25
        last_runtime = 0.01
        exponential_runtimes = np.exp(np.linspace(np.log(initial_runtime), np.log(last_runtime), sample_N))
        circle_settings = {
            "radius": 0.11,
            "color": WHITE,
            "fill_color": BLUE,
            "fill_opacity": 1.0,
            "stroke_width": 0.5,
        }
        line_settings = {
            "width": 1.6,
            "color": WHITE,
            "fill_opacity": 0.8,
        }
        (
            metabolic_network,
            nodes,
            edges,
            highlighted_edges,
            arrows_to_grow,
            full_object
        ) = Utils.create_metabolic_network(
            nodes_dict=new_nodes_dict,
            edges_dict=new_edges_dict,
            circle_settings=circle_settings,
            line_settings=line_settings,
            scale=0.18,
            expression_settings=None,
            paths=None,
            node_paths=node_paths
        )
        full_object.next_to(char_rect.get_left(), RIGHT, aligned_edge=LEFT).shift(LEFT * 0.2)
        full_object.move_to(char_rect.get_center())

        self.play(FadeIn(metabolic_network),
                  *[FadeIn(arrows) for arrows in arrows_to_grow],
                  run_time=2 * self.speed)

        purple_ = np.array([0.5, 0, 0.5])
        orange_ = np.array([1, 0.5, 0])
        alpha = 0.05

        def custom_line_indicate_animation_only_width(obj, color, scale_factor=2):
            assert (isinstance(obj, Line))
            current_color = obj.get_color()
            current_width = obj.get_stroke_width()
            new_width = current_width * scale_factor
            old_width = current_width * 1
            func = Succession(
                ApplyMethod(obj.set_stroke, color, new_width),
                ApplyMethod(obj.set_stroke, current_color, old_width),
            )
            return func

        def custom_node_indicate_animation(obj, color, scale_factor= 2):
            assert (isinstance(obj, Dot))
            current_color = obj.get_color()
            current_radius = obj.get_radius()
            new_radius = current_radius * scale_factor
            old_radius = current_radius * 1
            func = Succession(
                ApplyMethod(obj.set_color, color),
                ApplyMethod(obj.set_radius, new_radius),
                ApplyMethod(obj.set_color, current_color),
                ApplyMethod(obj.set_radius, old_radius),
            )
            return func

        dict_with_highlights_and_color_gradient = {}
        for path in highlighted_edges:
            for obj in path:
                dict_with_highlights_and_color_gradient[obj] = [0, 0]
        for idx in range(sample_N):
            cluster_number = np.random.randint(2)
            if cluster_number == 0:
                random_path_idx = np.random.randint(len(random_paths_J1))
                color = PURPLE
                for obj in highlighted_edges[random_path_idx]:
                    dict_with_highlights_and_color_gradient[obj][0] += 1 / sample_N
                    new_color = (color_to_rgb(obj.get_color()) + alpha * (purple_ - color_to_rgb(obj.get_color())))
                    obj.set_color(rgb_to_color(new_color))
                for arrow in arrows_to_grow:
                    new_color = (color_to_rgb(arrow.get_color()) + alpha * (purple_ - color_to_rgb(arrow.get_color())))
                    arrow.set_color(rgb_to_color(new_color))
            elif cluster_number == 1:
                random_path_idx = np.random.randint(len(random_paths_E4)) + len(random_paths_J1)
                color = ORANGE
                for obj in highlighted_edges[random_path_idx]:
                    dict_with_highlights_and_color_gradient[obj][1] += 1 / sample_N
                    new_color = (color_to_rgb(obj.get_color()) + alpha * (orange_ - color_to_rgb(obj.get_color())))
                    obj.set_color(rgb_to_color(new_color))
                for arrow in arrows_to_grow:
                    new_color = (color_to_rgb(arrow.get_color()) + alpha * (purple_ - color_to_rgb(arrow.get_color())))
                    arrow.set_color(rgb_to_color(new_color))
            run_time = exponential_runtimes[idx]
            nodes_in_highlighted_edges = []
            lines_in_highlighted_edges = []
            for obj in highlighted_edges[random_path_idx]:
                if isinstance(obj, Dot):
                    nodes_in_highlighted_edges.append(obj)
                elif isinstance(obj, Line):
                    lines_in_highlighted_edges.append(obj)

            self.play(
                *[custom_node_indicate_animation(
                    obj, color=color, scale_factor=2
                ) for obj in nodes_in_highlighted_edges],
                *[custom_line_indicate_animation_only_width(
                    obj, color=color, scale_factor=2)
                    for obj in lines_in_highlighted_edges],
                run_time=run_time * self.speed
            )

        nodes_to_indicate_and_fade_out = []
        lines_to_indicate_and_fade_out = []
        for obj in nodes.values():
            obj_color = color_to_rgb(obj.get_color())
            blue_plusminus = 0.20
            blue = color_to_rgb(BLUE)
            blue_lower = [blue[0] - blue_plusminus, blue[1] - blue_plusminus, blue[2] - blue_plusminus]
            blue_upper = [blue[0] + blue_plusminus, blue[1] + blue_plusminus, blue[2] + blue_plusminus]
            if (
                    blue_lower[0] <= obj_color[0] <= blue_upper[0] and
                    blue_lower[1] <= obj_color[1] <= blue_upper[1] and
                    blue_lower[2] <= obj_color[2] <= blue_upper[2]
            ):
                nodes_to_indicate_and_fade_out.append(obj)
        for obj in edges.values():
            obj_color = color_to_rgb(obj.get_color())
            if obj_color[0] > 0.8 and obj_color[1] > 0.8 and obj_color[2] > 0.8:
                if isinstance(obj, Line):
                    lines_to_indicate_and_fade_out.append(obj)

        self.play(
            *[custom_line_indicate_animation_only_width(
                obj, color=WHITE, scale_factor=2) for obj in lines_to_indicate_and_fade_out],
            run_time=1.5 * self.speed,
        )
        self.play(
            *[FadeOut(obj) for obj in nodes_to_indicate_and_fade_out],
            *[FadeOut(obj) for obj in lines_to_indicate_and_fade_out],
            run_time=1 * self.speed
        )
        full_subscene = VGroup(vgroup_3,
                               char_rect,
                               chararacteristics_text,
                               full_object)
        box = SurroundingRectangle(full_subscene, color=BLUE)
        box_1 = self.vom_dict["box_question_1"]
        box.stretch_to_fit_height(box_1.get_height())
        box.next_to(box_1, RIGHT, aligned_edge=UP)
        self.play(Write(box),
                  run_time=1 * self.speed)

        self.vom_dict["box_question_2"] = box
        self.vom_dict["characteristics_subscene"] = full_subscene
        subscene_minus_faded_out = VGroup()
        for obj in full_object:
            if obj not in nodes_to_indicate_and_fade_out + lines_to_indicate_and_fade_out:
                subscene_minus_faded_out.add(obj)

        self.vom_dict["characteristics_subscene_minus_faded_out"] = subscene_minus_faded_out
        self.vom_dict["char_rect"] = char_rect
        self.vom_dict["chararacteristics_text"] = chararacteristics_text
        self.vom_dict["box_1"] = box_1

    general_speed_multiplier = 1
    speed = 1 / general_speed_multiplier

    def construct(self):
        ### start
        self.vom_dict = {}
        # self.intro()
        self.does_gene_expression_predict_metabolic_activity()
        self.create_network_graph_subscene()
        box_1 = self.vom_dict["box_1"]
        char_rect = self.vom_dict["char_rect"]
        chararacteristics_text = self.vom_dict["chararacteristics_text"]
        subscene_minus_faded_out = self.vom_dict["characteristics_subscene_minus_faded_out"]
        box = self.vom_dict["box_question_2"]

        self.wait(1 * self.speed)

        box_1_copy = box_1.copy()
        box_1_copy.set_stroke(width=10)
        self.play(ShowPassingFlash(box_1_copy, time_width=0.5, run_time=2 * self.speed))
        self.wait(1 * self.speed)
        clustering_graph = self.vom_dict["clustering_graph"]
        self.play(FadeOut(subscene_minus_faded_out),
                  FadeOut(box),
                  FadeOut(self.vom_dict["prediction_question"]),
                  FadeOut(chararacteristics_text),
                  FadeOut(char_rect),
                  FadeOut(clustering_graph),
                  run_time=1 * self.speed)
        self.wait(1 * self.speed)

        self.play(
            FadeOut(self.vom_dict["vgroup2"]),
            FadeOut(self.vom_dict["reaction_table"]),
            FadeOut(self.vom_dict["metabolic_network"]),
            FadeOut(self.vom_dict["full_object"]),
            FadeOut(self.vom_dict["box_question_1"]),
            run_time=1 * self.speed
        )
        # TODO change indication in network graph to be only width using custom function
        # TODO and make speed slightly different


        # specific_question_text_3 = Text(
        #     "Do these differences resemble underlying biology?"
        # ).scale(0.5)

        # self.play(text_route_optimization.animate.shift(UP*3),
        #             run_time=1*self.speed)

        # metabolic_network = Text(
        #     "Metabolic Network",
        # ).scale(0.5)
        # gene_expression = Text(
        #     "Integrating gene expression",
        # ).scale(0.5)
        #
        #
        #
        # ## explain the problem with bulletpoints
        # bullet_points = VGroup(
        #     VGroup(
        #         Circle(radius=0.1, color=BLUE),
        #        Text("Metabolic Network"),
        #        Square(side_length=0.5, color=BLUE)
        #     ).arrange(RIGHT),
        #     VGroup(Text("Metabolic Tasks"), Square(side_length=0.5, color=BLUE)),
        #     VGroup(Text("Integrating gene expression"), Square(side_length=0.5, color=BLUE)),
        #     VGroup(Text("Algorithms"), Square(side_length=0.5, color=BLUE)),
        # )
        # bullet_points.arrange(DOWN, aligned_edge=LEFT)
        # bullet_points.next_to(text_route_optimization, DOWN).shift(LEFT)
        # self.play(Write(bullet_points),
        #           run_time=4*self.speed)
        #
        # ###
        # flux_minimization_square = Square(
        #     side_length=2,
        #     color=BLUE
        # )
        # flux_minimization_text = Text(
        #     "Flux Minimization",
        # ).scale(0.5)
        # flux_minimization_text.next_to(flux_minimization_square, UP)
        # flux_group = VGroup(flux_minimization_square, flux_minimization_text)
        #
        # self.play(ShowCreation(flux_minimization_square),
        #           Write(flux_minimization_text),
        #           run_time=2*self.speed)
        # self.play(FadeOut(text_route_optimization),
        #           run_time=1*self.speed)
        # self.play(flux_group.animate.scale(3),
        #           run_time=2*self.speed)
        #


if __name__ == "__main__":
    subprocess.run(["manimgl", "SRC/main.py", "Main", "-f",
                    # "--full_screen"
                    ])
    # subprocess.run([
    #     "manimgl", "SRC/main.py", "Main",
    #     "-w",
    #     "--uhd"
    # ])



    # checkpoint_paste()
