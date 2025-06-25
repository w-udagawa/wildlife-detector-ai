# Wildlife Detector AI - File Organization Update

## 📅 Update Date: 2025-06-25

## ✅ Completed Features

### 1. File Move Operation
- **Changed from Copy to Move**
  - Files are now moved instead of copied
  - Original files are removed from source location
  - Warning message updated accordingly

### 2. Post-Detection Organization
- **CSV Import Feature**
  - New menu item: "Import detection results from CSV"
  - Allows loading previous detection results
  - Supports both absolute and relative file paths

- **Organize from CSV**
  - New button: "Organize from CSV"
  - Can organize files based on imported CSV results
  - Automatically resolves relative paths from CSV location

### 3. Enhanced Organization Dialog
- **Output Directory Selection**
  - Users must select destination folder
  - No longer uses default output directory automatically
  - Provides better control over file organization

## 📊 Usage Instructions

### Method 1: Organize After Detection
1. Run detection on images
2. Click "📁 File Organization" button in Results tab
3. Select destination folder
4. Files will be moved to species-specific folders

### Method 2: Organize from CSV
1. Menu → File → "Import detection results from CSV"
2. Select a previously exported CSV file
3. Click "📄 Organize from CSV" button
4. Select destination folder
5. Files will be moved based on CSV data

## ⚠️ Important Notes

- **Files are MOVED, not copied**
  - Original files will be removed
  - Consider backing up before organization
  
- **File Path Resolution**
  - Relative paths in CSV are resolved from CSV location
  - Missing files will trigger a warning dialog
  
- **Folder Structure**
  ```
  destination_folder/
  ├── Corvus_macrorhynchos/    # Species folders
  ├── Ardea_sp/
  ├── no_detection/             # No detections
  └── low_confidence/           # Below threshold
  ```

## 🔧 Technical Details

### Modified Files
1. `/gui/main_window.py`
   - Added CSV import functionality
   - Changed file operation to move
   - Added output directory selection

2. `/utils/csv_exporter.py`
   - Added `import_from_csv()` method
   - Handles multiple detections per image
   - Parses bounding box data

3. `/utils/file_manager.py`
   - Already supported move operation
   - Summary file now in English

### CSV Import Format
The CSV importer expects the standard Wildlife Detector output format:
- Image File
- Detection Count
- Species Name
- Scientific Name
- Common Name
- Category
- Confidence
- Bounding Box
- Processing Time (s)
- Status
- Error Message

---

**Updated by**: Claude
**Status**: Ready for use
