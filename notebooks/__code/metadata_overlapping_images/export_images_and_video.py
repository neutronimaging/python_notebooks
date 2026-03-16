import os
from pathlib import Path
import tifffile
import imageio
import numpy as np
import pyqtgraph.exporters
from IPython.display import HTML, display
from PIL import Image
from qtpy import QtCore, QtGui
from qtpy.QtWidgets import QApplication


class ExportImagesAndVideo:
    ext = ".png"
    ext_video = ".mp4"

    list_of_images_exported = []

    def __init__(self, parent=None, export_folder=""):
        self.parent = parent
        self.export_folder = export_folder
        self._check_video_dependencies()

    def _check_video_dependencies(self):
        """Check if required video creation dependencies are available."""
        try:
            import imageio
            print(f"imageio version: {imageio.__version__}")
            
            # Check available plugins
            plugins = imageio.plugins.get_plugin_names()
            if 'ffmpeg' in plugins:
                print("FFMPEG plugin available for video creation")
            else:
                print("Warning: FFMPEG plugin not found. Video creation may fail.")
                
        except Exception as e:
            print(f"Warning: Video dependency check failed: {e}")

    def _create_output_file_name(self, file=""):
        if file == "":
            return ""

        basename_ext = os.path.basename(file)
        [basename, ext] = os.path.splitext(basename_ext)

        full_file_name = os.path.join(self.export_folder, basename + self.ext)
        return full_file_name

    def _create_output_video_name(self, extension=".mp4"):
        base_name = "exported_video"
        video_file_name = os.path.join(self.export_folder, base_name + extension)
        return video_file_name

    def _create_output_avi_name(self):
        """Create output filename for AVI video."""
        return self._create_output_video_name(".avi")

    def run(self):
        self.export_images()
        self.export_video()
        
    def export_images(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.parent.eventProgress.setMinimum(1)
        self.parent.eventProgress.setMaximum(len(self.parent.data_dict["file_name"]))
        self.parent.eventProgress.setValue(1)
        self.parent.eventProgress.setVisible(True)

        self.list_of_images_exported = []
        
        for _index, _file in enumerate(self.parent.data_dict["file_name"]):
            output_file_name = self._create_output_file_name(file=_file)
            self.list_of_images_exported.append(output_file_name)
            
            self.parent.ui.file_slider.setValue(_index)

            exporter = pyqtgraph.exporters.ImageExporter(self.parent.ui.image_view.view)

            exporter.params.param("width").setValue(2024, blockSignal=exporter.widthChanged)
            exporter.params.param("height").setValue(2014, blockSignal=exporter.heightChanged)

            exporter.export(output_file_name)

            self.parent.eventProgress.setValue(_index + 2)
            QtGui.QGuiApplication.processEvents()

        QtGui.QGuiApplication.processEvents()

        display(HTML(f"Exported Images in Folder {self.export_folder}"))
        self.parent.eventProgress.setVisible(False)
        QApplication.restoreOverrideCursor()

    def load_tiff_images_to_stack(self, image_files, output_stack_path=None):
        """
        Load a list of TIFF images and combine them into a single TIFF stack.
        
        Args:
            image_files (list): List of file paths to TIFF images
            output_stack_path (str, optional): Path for output TIFF stack. 
                                             If None, uses default name in export folder.
        
        Returns:
            str: Path to the created TIFF stack file
        """
        if not image_files:
            raise ValueError("No image files provided")
        
        # Set default output path if not provided
        if output_stack_path is None:
            output_stack_path = os.path.join(self.export_folder, "image_stack.tiff")
        
        print(f"Loading {len(image_files)} images into TIFF stack...")
        
        # Load first image to get dimensions and create stack
        first_image = Image.open(image_files[0])
        
        # # Convert first image to numpy array if needed
        # if hasattr(first_image, 'mode') and first_image.mode != 'RGB':
        #     first_image = first_image.convert('RGB')
        
        # Collect all images
        images = [first_image]
        
        for i, img_path in enumerate(image_files[1:], 1):
            print(f"Loading image {i+1}/{len(image_files)}: {os.path.basename(img_path)}")
            img = Image.open(img_path)
            
            # # Ensure consistent mode
            # if hasattr(img, 'mode') and img.mode != first_image.mode:
            #     img = img.convert(first_image.mode)
            
            images.append(img)
        
        # Save as multi-page TIFF
        print(f"Saving TIFF stack to: {output_stack_path}")
        first_image.save(
            output_stack_path,
            save_all=True,
            append_images=images[1:],
            compression='tiff_lzw'  # Optional compression
        )
        
        print(f"Successfully created TIFF stack with {len(images)} images")
        return output_stack_path

    def load_tiff_images_from_folder(self, folder_path, pattern="*.tiff"):
        """
        Load all TIFF images from a folder.
        
        Args:
            folder_path (str): Path to folder containing TIFF images
            pattern (str): Glob pattern for image files (default: "*.tiff")
        
        Returns:
            list: Sorted list of image file paths
        """
        folder = Path(folder_path)
        
        # Support multiple TIFF extensions
        patterns = [pattern, "*.tif", "*.TIF", "*.TIFF"]
        image_files = []
        
        for pat in patterns:
            image_files.extend(folder.glob(pat))
        
        # Sort files naturally by name
        image_files = sorted([str(f) for f in image_files])
        
        print(f"Found {len(image_files)} TIFF images in {folder_path}")
        return image_files

    def export_video(self):
        """
        Create a TIFF stack from exported images, then convert to MPEG video.
        """
        # reload the images as a stack of TIFFs and then export as video
        list_of_images_exported = self.list_of_images_exported
        
        if not list_of_images_exported:
            print("No images have been exported yet. Please run export_images() first.")
            return
        
        # Create TIFF stack from exported images
        tiff_stack_path = self.load_tiff_images_to_stack(
            list_of_images_exported, 
            os.path.join(self.export_folder, "exported_images_stack.tiff")
        )
        
        display(HTML(f"Created TIFF stack: {tiff_stack_path}"))
        
        # Export video from TIFF stack
        print("Converting TIFF stack to MPEG video...")
        
        # retrieving the frame rate
        frame_rate = self.parent.ui.frames_per_second_spinBox.value()
        print(f"Using frame rate: {frame_rate} fps")

        # Create both MP4 and AVI versions
        mp4_path = self.create_mp4_from_tiff_stack(tiff_stack_path, fps=frame_rate)
        avi_path = self.create_avi_from_tiff_stack(tiff_stack_path, fps=frame_rate)
        
        if mp4_path:
            display(HTML(f"Created MP4 video: {mp4_path}"))
        if avi_path:
            display(HTML(f"Created AVI video (ImageJ-style): {avi_path}"))
            
        # return {"mp4": mp4_path, "avi": avi_path}

    def create_avi_from_tiff_stack(self, tiff_stack_path, output_avi_path=None, fps=10, codec="MJPG", preserve_grayscale=True):
        """
        Create an AVI video from TIFF stack, similar to ImageJ's AVI export.
        
        Args:
            tiff_stack_path (str): Path to the TIFF stack file
            output_avi_path (str, optional): Output AVI path. If None, uses default naming.
            fps (int): Frames per second (ImageJ default is often 7-10 fps)
            codec (str): Video codec - options: "MJPG" (MJPEG), "XVID", "Uncompressed"
            preserve_grayscale (bool): Keep grayscale format when possible
        
        Returns:
            str: Path to created AVI file, or None if failed
        """
        if not os.path.exists(tiff_stack_path):
            print(f"TIFF stack not found: {tiff_stack_path}")
            return None
        
        if output_avi_path is None:
            output_avi_path = self._create_output_avi_name()
        
        print(f"Creating ImageJ-style AVI from TIFF stack: {tiff_stack_path}")
        print(f"Codec: {codec}, FPS: {fps}, Preserve grayscale: {preserve_grayscale}")
        
        try:
            stack = tifffile.imread(tiff_stack_path)
            print(f"Loaded TIFF stack with shape: {stack.shape}, dtype: {stack.dtype}")
            
            # Choose the appropriate codec settings
            codec_params = self._get_avi_codec_params(codec)
            
            # Create AVI writer with ImageJ-like settings
            writer = imageio.get_writer(
                output_avi_path,
                format='FFMPEG',
                mode='I',
                fps=fps,
                **codec_params
            )
            
            frame_count = stack.shape[0] if stack.ndim >= 3 else 1
            print(f"Processing {frame_count} frames for AVI...")
            
            # Process frames with ImageJ-like approach
            for i in range(frame_count):
                frame = stack[i] if stack.ndim >= 3 else stack
                processed_frame = self._process_frame_for_avi(frame, preserve_grayscale, codec)
                writer.append_data(processed_frame)
                
                if (i + 1) % max(1, frame_count // 10) == 0:
                    print(f"Processed {i+1}/{frame_count} frames...")
            
            writer.close()
            print(f"Successfully created AVI video: {output_avi_path}")
            return output_avi_path
            
        except Exception as e:
            print(f"Error creating AVI video: {str(e)}")
            return None
    
    def _get_avi_codec_params(self, codec):
        """Get codec parameters for AVI creation, mimicking ImageJ options."""
        codec_upper = codec.upper()
        
        if codec_upper == "MJPG" or codec_upper == "MJPEG":
            # MJPEG - good compression, high quality (ImageJ's most common choice)
            return {
                'codec': 'mjpeg',
                'quality': 9,  # High quality
                'ffmpeg_params': ['-pix_fmt', 'yuvj420p']  # JPEG color space
            }
        elif codec_upper == "XVID":
            # XVID codec
            return {
                'codec': 'libxvid',
                'quality': 2,  # Very high quality for XVID
                'ffmpeg_params': ['-pix_fmt', 'yuv420p']
            }
        elif codec_upper == "UNCOMPRESSED" or codec_upper == "RAW":
            # Uncompressed (large files but perfect quality)
            return {
                'codec': 'rawvideo',
                'ffmpeg_params': ['-pix_fmt', 'rgb24']  # Raw RGB
            }
        else:
            # Default to MJPEG
            print(f"Unknown codec '{codec}', using MJPEG")
            return self._get_avi_codec_params("MJPG")
    
    def _process_frame_for_avi(self, frame, preserve_grayscale=True, codec="MJPG"):
        """Process a single frame for AVI export, similar to ImageJ."""
        
        # Handle different bit depths like ImageJ does
        if frame.dtype == np.uint16:
            # 16-bit to 8-bit conversion (ImageJ approach)
            # Use the full dynamic range of the image
            frame_min, frame_max = frame.min(), frame.max()
            if frame_max > frame_min:
                frame_8bit = ((frame - frame_min) / (frame_max - frame_min) * 255).astype(np.uint8)
            else:
                frame_8bit = np.zeros_like(frame, dtype=np.uint8)
        elif frame.dtype == np.float32 or frame.dtype == np.float64:
            # Float to 8-bit
            frame_8bit = np.clip(frame * 255, 0, 255).astype(np.uint8)
        else:
            # Already 8-bit or convert to 8-bit
            frame_8bit = frame.astype(np.uint8)
        
        # Handle grayscale preservation like ImageJ
        if preserve_grayscale and len(frame_8bit.shape) == 2:
            # For grayscale, convert to RGB but keep it visually grayscale
            # This is how ImageJ handles grayscale in AVI
            rgb_frame = np.stack([frame_8bit] * 3, axis=-1)
        elif len(frame_8bit.shape) == 2:
            # Force to RGB even for grayscale
            rgb_frame = np.stack([frame_8bit] * 3, axis=-1)
        else:
            # Already RGB or multi-channel
            rgb_frame = frame_8bit
            
        return rgb_frame
    
    def create_mp4_from_tiff_stack(self, tiff_stack_path, output_mp4_path=None, fps=20):
        """Create MP4 video from TIFF stack (existing functionality kept separate)."""
        
        if output_mp4_path is None:
            output_mp4_path = self._create_output_video_name(".mp4")
            
        print(f"Creating MP4 from TIFF stack: {tiff_stack_path}")
        
        try:
            stack = tifffile.imread(tiff_stack_path)
            
            writer = imageio.get_writer(
                output_mp4_path,
                format='FFMPEG',
                mode='I',
                fps=fps,
                codec='libx264',
                quality=9,
                ffmpeg_params=['-pix_fmt', 'yuv420p']
            )
            
            # Global normalization for consistent brightness
            if stack.ndim >= 3:
                flat = stack.reshape(-1)
                p_low, p_high = np.percentile(flat, (0.5, 99.5))
            else:
                p_low, p_high = np.percentile(stack, (0.5, 99.5))
            
            frame_count = stack.shape[0] if stack.ndim >= 3 else 1
            
            for i in range(frame_count):
                frame = stack[i] if stack.ndim >= 3 else stack
                
                # Normalize to 8-bit
                if frame.dtype != np.uint8:
                    f = frame.astype(np.float64)
                    f = np.clip((f - p_low) / max(p_high - p_low, 1e-12), 0, 1)
                    frame8 = (f * 255).astype(np.uint8)
                else:
                    frame8 = frame
                
                # Convert to RGB
                if len(frame8.shape) == 2:
                    rgb = np.stack([frame8] * 3, axis=-1)
                else:
                    rgb = frame8
                
                writer.append_data(rgb)
            
            writer.close()
            print(f"Successfully created MP4: {output_mp4_path}")
            return output_mp4_path
            
        except Exception as e:
            print(f"Error creating MP4: {str(e)}")
            return None
        
    def export_avi_like_imagej(self, tiff_stack_path=None, codec="MJPG", fps=10, quality="High"):
        """
        Export AVI video with ImageJ-like options and interface.
        
        Args:
            tiff_stack_path (str, optional): Path to TIFF stack. If None, uses last exported stack.
            codec (str): Video codec - \"MJPG\" (default), \"XVID\", \"Uncompressed\"
            fps (int): Frames per second (ImageJ typically uses 7-10)
            quality (str): \"High\", \"Medium\", \"Low\" - affects compression settings
        
        Returns:
            str: Path to created AVI file
        """
        
        # Use existing stack or create from exported images
        if tiff_stack_path is None:
            if not self.list_of_images_exported:
                print("No images exported. Please run export_images() first.")
                return None
            
            print("Creating TIFF stack from exported images...")
            tiff_stack_path = self.load_tiff_images_to_stack(
                self.list_of_images_exported,
                os.path.join(self.export_folder, "exported_images_stack.tiff")
            )
        
        # ImageJ-style quality settings
        quality_settings = {
            "High": {"fps": fps, "codec": codec},
            "Medium": {"fps": fps, "codec": "MJPG"},  # Force MJPG for medium
            "Low": {"fps": max(fps - 3, 5), "codec": "MJPG"}  # Lower FPS for smaller files
        }
        
        settings = quality_settings.get(quality, quality_settings["High"])
        
        print("=" * 50)
        print("ImageJ-Style AVI Export")
        print("=" * 50)
        print(f"Codec: {settings['codec']}")
        print(f"Frame Rate: {settings['fps']} fps")
        print(f"Quality: {quality}")
        print(f"Input: {os.path.basename(tiff_stack_path)}")
        print("=" * 50)
        
        # Create AVI with ImageJ-like settings
        avi_path = self.create_avi_from_tiff_stack(
            tiff_stack_path=tiff_stack_path,
            fps=settings['fps'],
            codec=settings['codec'],
            preserve_grayscale=True  # ImageJ preserves grayscale when possible
        )
        
        if avi_path:
            # Display ImageJ-like success message
            file_size = os.path.getsize(avi_path) / (1024 * 1024)  # MB
            print(f"\n✓ AVI Export Complete!")
            print(f"  File: {os.path.basename(avi_path)}")
            print(f"  Size: {file_size:.1f} MB")
            print(f"  Location: {self.export_folder}")
            
            display(HTML(f"<b>ImageJ-style AVI created:</b> {avi_path} ({file_size:.1f} MB)"))
        
        return avi_path
        