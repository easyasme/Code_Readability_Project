import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
                             QLabel, QLineEdit, QTextEdit, QMessageBox, QSpinBox, QCheckBox,
                             QScrollArea, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PIL import Image

class InpaintingLabel(QLabel):
    brush_size_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drawing = False
        self.last_point = None
        self.mask = None
        self.brush_size = 5

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.pixmap())
            painter.setPen(QPen(Qt.red, self.brush_size, Qt.SolidLine))
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.update()

            if self.mask is None:
                size = self.pixmap().size()
                self.mask = np.zeros((size.height(), size.width()), dtype=np.uint8)
            cv2.line(self.mask, (self.last_point.x(), self.last_point.y()),
                     (event.pos().x(), event.pos().y()), (255, 255, 255), self.brush_size)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.brush_size = min(50, self.brush_size + 1)
            else:
                self.brush_size = max(1, self.brush_size - 1)
            self.brush_size_changed.emit(self.brush_size)
            event.accept()
        else:
            super().wheelEvent(event)

class ImageViewerTab(QWidget):
    image_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.image_files = []
        self.current_image_index = -1
        self.current_image = None
        self.aspect_ratio = 1.0
        self.updating = False
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Directory selection
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("No directory selected")
        dir_layout.addWidget(self.dir_label)
        self.select_dir_btn = QPushButton("Select Directory")
        self.select_dir_btn.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.select_dir_btn)
        main_layout.addLayout(dir_layout)

        # Create a splitter for image preview and caption/template area
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter, 1)  # Give it a stretch factor

        # Image display
        image_widget = QWidget()
        image_layout = QVBoxLayout(image_widget)
        self.scroll_area = QScrollArea()
        self.image_display = InpaintingLabel()
        self.image_display.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_display)
        self.scroll_area.setWidgetResizable(True)
        image_layout.addWidget(self.scroll_area)

        # Brush size control
        brush_size_layout = QHBoxLayout()
        brush_size_layout.addWidget(QLabel("Brush Size:"))
        self.brush_size_spinner = QSpinBox()
        self.brush_size_spinner.setRange(1, 50)
        self.brush_size_spinner.setValue(5)
        self.brush_size_spinner.valueChanged.connect(self.change_brush_size)
        brush_size_layout.addWidget(self.brush_size_spinner)
        image_layout.addLayout(brush_size_layout)

        splitter.addWidget(image_widget)

        # Image info
        info_layout = QHBoxLayout()
        self.resolution_label = QLabel("Resolution: ")
        info_layout.addWidget(self.resolution_label)
        image_layout.addLayout(info_layout)

        # Resize options
        resize_layout = QHBoxLayout()
        self.width_input = QSpinBox()
        self.width_input.setRange(1, 10000)
        self.width_input.valueChanged.connect(self.width_changed)
        resize_layout.addWidget(QLabel("Width:"))
        resize_layout.addWidget(self.width_input)
        self.height_input = QSpinBox()
        self.height_input.setRange(1, 10000)
        self.height_input.valueChanged.connect(self.height_changed)
        resize_layout.addWidget(QLabel("Height:"))
        resize_layout.addWidget(self.height_input)
        self.maintain_aspect_checkbox = QCheckBox("Maintain Aspect Ratio")
        self.maintain_aspect_checkbox.setChecked(True)
        resize_layout.addWidget(self.maintain_aspect_checkbox)
        self.resize_btn = QPushButton("Resize")
        self.resize_btn.clicked.connect(self.resize_image)
        resize_layout.addWidget(self.resize_btn)
        image_layout.addLayout(resize_layout)

        splitter.addWidget(image_widget)

        # Caption and template input
        caption_template_widget = QWidget()
        caption_template_layout = QHBoxLayout(caption_template_widget)
        
        # Caption input
        caption_layout = QVBoxLayout()
        caption_layout.addWidget(QLabel("Caption:"))
        self.caption_input = QTextEdit()
        caption_layout.addWidget(self.caption_input)
        self.save_caption_btn = QPushButton("Save Caption")
        self.save_caption_btn.clicked.connect(self.save_caption)
        caption_layout.addWidget(self.save_caption_btn)
        caption_template_layout.addLayout(caption_layout)

        # Template input
        template_layout = QVBoxLayout()
        template_layout.addWidget(QLabel("Caption Template:"))
        self.template_input = QTextEdit()
        self.template_input.setPlaceholderText("Enter caption template. Use {{variable}} for placeholders.")
        template_layout.addWidget(self.template_input)
        self.apply_template_btn = QPushButton("Apply Template")
        self.apply_template_btn.clicked.connect(self.apply_template)
        template_layout.addWidget(self.apply_template_btn)
        caption_template_layout.addLayout(template_layout)

        splitter.addWidget(caption_template_widget)

        # Set initial sizes for the splitter
        splitter.setSizes([700, 100])  # Adjust these values as needed

        # Inpainting
        inpaint_layout = QHBoxLayout()
        self.inpaint_btn = QPushButton("Inpaint")
        self.inpaint_btn.clicked.connect(self.inpaint_image)
        inpaint_layout.addWidget(self.inpaint_btn)
        self.clear_mask_btn = QPushButton("Clear Mask")
        self.clear_mask_btn.clicked.connect(self.clear_inpaint_mask)
        inpaint_layout.addWidget(self.clear_mask_btn)
        self.save_btn = QPushButton("Save Inpainted Image")
        self.save_btn.clicked.connect(self.save_image)
        inpaint_layout.addWidget(self.save_btn)
        main_layout.addLayout(inpaint_layout)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.show_previous_image)
        nav_layout.addWidget(self.prev_btn)
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.show_next_image)
        nav_layout.addWidget(self.next_btn)
        main_layout.addLayout(nav_layout)

        # Add delete button
        self.delete_btn = QPushButton("Delete Current Image")
        self.delete_btn.clicked.connect(self.delete_current_image)
        nav_layout.addWidget(self.delete_btn)

        self.image_changed.connect(self.update_image_info)
        self.image_display.brush_size_changed.connect(self.update_brush_size_spinner)

    def change_brush_size(self, size):
        self.image_display.brush_size = size

    def update_brush_size_spinner(self, size):
        self.brush_size_spinner.setValue(size)

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.dir_label.setText(dir_path)
            self.load_images(dir_path)

    def load_images(self, directory):
        self.image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if self.image_files:
            self.current_image_index = 0
            self.show_current_image()
        else:
            QMessageBox.warning(self, "Error", "No images found in the selected directory.")

    def show_current_image(self):
        if 0 <= self.current_image_index < len(self.image_files):
            image_path = os.path.join(self.dir_label.text(), self.image_files[self.current_image_index])
            self.current_image = cv2.imread(image_path)
            self.display_image(self.current_image)
            self.image_changed.emit()

    def display_image(self, img):
        if img is not None:
            height, width, channel = img.shape
            bytes_per_line = 3 * width
            q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format_BGR888)
            pixmap = QPixmap.fromImage(q_image)
            self.image_display.setPixmap(pixmap)
            self.image_display.mask = None

    def show_previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.show_current_image()

    def show_next_image(self):
        if self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.show_current_image()

    def update_image_info(self):
        if self.current_image is not None:
            height, width = self.current_image.shape[:2]
            self.resolution_label.setText(f"Resolution: {width}x{height}")
            self.updating = True  # Set the flag before updating
            self.width_input.setValue(width)
            self.height_input.setValue(height)
            self.updating = False  # Reset the flag after updating
            self.aspect_ratio = width / height

    def width_changed(self, width):
        if not self.updating and self.maintain_aspect_checkbox.isChecked():
            self.updating = True
            self.height_input.setValue(int(width / self.aspect_ratio))
            self.updating = False

    def height_changed(self, height):
        if not self.updating and self.maintain_aspect_checkbox.isChecked():
            self.updating = True
            self.width_input.setValue(int(height * self.aspect_ratio))
            self.updating = False

    def update_height(self, width):
        if self.maintain_aspect_checkbox.isChecked():
            self.height_input.setValue(int(width / self.aspect_ratio))

    def update_width(self, height):
        if self.maintain_aspect_checkbox.isChecked():
            self.width_input.setValue(int(height * self.aspect_ratio))

    def resize_image(self):
        if self.current_image is not None:
            new_width = self.width_input.value()
            new_height = self.height_input.value()
            
            reply = QMessageBox.question(self, 'Confirm Resize and Overwrite',
                                        f"Are you sure you want to resize and overwrite the original image?\n"
                                        f"Current size: {self.current_image.shape[1]}x{self.current_image.shape[0]}\n"
                                        f"New size: {new_width}x{new_height}",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                resized_image = cv2.resize(self.current_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
                
                # Update the current image
                self.current_image = resized_image
                
                # Save the resized image, overwriting the original
                current_file = self.image_files[self.current_image_index]
                file_path = os.path.join(self.dir_label.text(), current_file)
                
                success = cv2.imwrite(file_path, self.current_image)
                
                if success:
                    self.display_image(self.current_image)
                    self.image_changed.emit()
                    QMessageBox.information(self, "Success", f"Image resized and saved, overwriting the original: {file_path}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save the resized image.")

    def save_caption(self):
        if self.current_image is not None:
            caption = self.caption_input.toPlainText()
            image_name = os.path.splitext(self.image_files[self.current_image_index])[0]
            caption_file = os.path.join(self.dir_label.text(), f"{image_name}.txt")
            with open(caption_file, "w") as f:
                f.write(caption)
            QMessageBox.information(self, "Success", f"Caption saved to {caption_file}")

    def apply_template(self):
        if self.current_image is not None:
            template = self.template_input.toPlainText()
            image_name = os.path.splitext(self.image_files[self.current_image_index])[0]
            caption = template.replace("{{filename}}", image_name)
            self.caption_input.setPlainText(caption)

    def inpaint_image(self):
        if self.current_image is not None and self.image_display.mask is not None:
            inpainted_image = cv2.inpaint(self.current_image, self.image_display.mask, 3, cv2.INPAINT_TELEA)
            self.current_image = inpainted_image
            self.display_image(self.current_image)
            self.image_changed.emit()

    def save_image(self):
        if self.current_image is not None:
            current_file = self.image_files[self.current_image_index]
            file_path = os.path.join(self.dir_label.text(), current_file)
            
            reply = QMessageBox.question(self, 'Confirm Overwrite',
                                        f"Are you sure you want to overwrite the original image?\n{file_path}",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Save the image in BGR format (OpenCV default)
                success = cv2.imwrite(file_path, self.current_image)
                if success:
                    QMessageBox.information(self, "Success", f"Image saved successfully, overwriting the original: {file_path}")
                    # Reload the saved image to ensure consistency
                    self.current_image = cv2.imread(file_path)
                    self.display_image(self.current_image)
                else:
                    QMessageBox.warning(self, "Error", "Failed to save the image.")

    def delete_current_image(self):
        if self.current_image is not None and 0 <= self.current_image_index < len(self.image_files):
            current_file = self.image_files[self.current_image_index]
            file_path = os.path.join(self.dir_label.text(), current_file)
            
            reply = QMessageBox.question(self, 'Confirm Delete',
                                        f"Are you sure you want to delete this image?\n{file_path}",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                try:
                    os.remove(file_path)
                    QMessageBox.information(self, "Success", f"Image deleted successfully: {file_path}")
                    
                    # Remove the deleted file from the list and update the display
                    del self.image_files[self.current_image_index]
                    
                    if len(self.image_files) == 0:
                        self.current_image_index = -1
                        self.current_image = None
                        self.image_display.clear()
                        self.image_changed.emit()
                    elif self.current_image_index >= len(self.image_files):
                        self.current_image_index = len(self.image_files) - 1
                        self.show_current_image()
                    else:
                        self.show_current_image()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to delete the image: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "No image selected or invalid image index.")

    def clear_inpaint_mask(self):
        if self.current_image is not None:
            self.image_display.mask = None
            self.display_image(self.current_image)