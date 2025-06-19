# """Page for uploading csv or excel files ETL then save to database."""

# import io

# import pandas as pd
# import streamlit as st

# st.set_page_config(page_title="File Upload", page_icon="📁")


# # Initialize session state
# def init_session_state() -> None:
#     """Initialize session state for file upload workflow."""
#     if "upload_workflow" not in st.session_state:
#         st.session_state.upload_workflow = {
#             "files": [],
#             "current_step": "upload",
#             "header_mappings": {},
#             "file_type": None,
#             "preview_data": {},
#             "processing_status": {},
#             "detected_separators": {},
#             "auto_suggestions": {},
#         }


# def reset_workflow() -> None:
#     """Reset the entire workflow state."""
#     st.session_state.upload_workflow = {
#         "files": [],
#         "current_step": "upload",
#         "header_mappings": {},
#         "file_type": None,
#         "preview_data": {},
#         "processing_status": {},
#         "detected_separators": {},
#         "auto_suggestions": {},
#     }


# def detect_file_type_and_separator(file) -> tuple[str, str, dict]:
#     """Auto-detect file type and separator based on filename and content."""
#     filename = file.name.lower()

#     # Reset file pointer
#     file.seek(0)
#     sample_content = file.read(2000).decode("utf-8", errors="ignore")
#     file.seek(0)

#     auto_suggestions = {}

#     # Detect by filename patterns
#     if "retailer" in filename or "organisasi" in filename:
#         file_type = "retailer"
#         separator = "|" if "|" in sample_content else ","
#         auto_suggestions = {
#             "ORGANIZATION ID": "retailer_id",
#             "ORGANIZATION NAME": "retailer_name",
#             "PERMANENTADDRES_STREET ADDRESS": "address",
#             "CONTACT NUMBER": "contact_info",
#             "STATUS": "status",
#         }
#     elif "sellin" in filename or "distribusi" in filename:
#         file_type = "sellin"
#         separator = "|" if "|" in sample_content else ","
#         auto_suggestions = {
#             "TRANSACTION DATETIME": "transaction_date",
#             "TRANSACTION ID": "transaction_id",
#             "DEST_ORGANIZATIONNAME": "retailer_name",
#             "PRODUCT NAME": "product_name",
#             "QTY": "quantity",
#             "FINAL VALUE": "amount",
#         }
#     elif "transaksi" in filename or "transaction" in filename:
#         file_type = "transaction"
#         separator = "," if "," in sample_content else "|"
#         auto_suggestions = {
#             "DateTime": "transaction_date",
#             "Transaction ID": "transaction_id",
#             "Organization Name": "retailer_name",
#             "Product Name": "product_name",
#             "Amount_Debit(IDR)": "amount",
#         }
#     elif "transfer" in filename:
#         file_type = "transfer"
#         separator = "," if "," in sample_content else "|"
#         auto_suggestions = {
#             "DateTime": "transaction_date",
#             "Transaction ID": "transaction_id",
#             "Organization Name": "from_retailer",
#             "Credit Party Name": "to_retailer",
#             "Amount": "amount",
#         }
#     elif "dsevisit" in filename or "visit" in filename:
#         file_type = "visit"
#         separator = "," if "," in sample_content else "|"
#         auto_suggestions = {
#             "Visit Date": "visit_date",
#             "Outlet Name": "retailer_name",
#             "DSE Name": "dse_name",
#             "Visit Status": "status",
#         }
#     else:
#         file_type = "other"
#         # Auto-detect separator
#         if sample_content.count("|") > sample_content.count(","):
#             separator = "|"
#         else:
#             separator = ","
#         auto_suggestions = {}

#     return file_type, separator, auto_suggestions


# def read_file_sample(file, separator: str = ",") -> pd.DataFrame | None:
#     """Read first 5 rows of file for preview and header detection."""
#     try:
#         file.seek(0)
#         if file.name.endswith(".csv"):
#             # Skip metadata rows for specific formats
#             content = file.read().decode("utf-8", errors="ignore")
#             file.seek(0)

#             # Skip header lines that start with quotes or metadata
#             lines = content.split("\n")
#             data_start = 0

#             for i, line in enumerate(lines):
#                 if (
#                     line.strip()
#                     and not line.startswith('"')
#                     or "|" in line
#                     or line.count(",") > 3
#                 ):
#                     data_start = i
#                     break

#             # Read from data start
#             if data_start > 0:
#                 content_from_data = "\n".join(lines[data_start:])
#                 return pd.read_csv(
#                     io.StringIO(content_from_data), sep=separator, nrows=5
#                 )
#             else:
#                 return pd.read_csv(file, sep=separator, nrows=5)

#         elif file.name.endswith((".xlsx", ".xls")):
#             return pd.read_excel(file, nrows=5)
#         return None
#     except Exception as e:
#         st.error(f"Error reading {file.name}: {e}")
#         return None


# def step_1_upload() -> None:
#     """Step 1: File upload with auto-detection."""
#     st.header("📁 Upload Data Files", divider=True)

#     uploaded_files = st.file_uploader(
#         "Choose data files",
#         accept_multiple_files=True,
#         type=["csv", "xlsx", "xls"],
#         help="Supported: CSV (comma/pipe separated), Excel files",
#         key="file_uploader",
#     )

#     if uploaded_files:
#         # Auto-detect file types and separators
#         detected_info = {}
#         for file in uploaded_files:
#             file_type, separator, auto_suggestions = detect_file_type_and_separator(
#                 file
#             )
#             detected_info[file.name] = {
#                 "type": file_type,
#                 "separator": separator,
#                 "suggestions": auto_suggestions,
#             }

#         # Store in session state
#         st.session_state.upload_workflow["files"] = uploaded_files
#         st.session_state.upload_workflow["detected_separators"] = {
#             f.name: detected_info[f.name]["separator"] for f in uploaded_files
#         }
#         st.session_state.upload_workflow["auto_suggestions"] = {
#             f.name: detected_info[f.name]["suggestions"] for f in uploaded_files
#         }
#         st.session_state.upload_workflow["current_step"] = "headers"

#         # Show detection results
#         st.success(f"✅ {len(uploaded_files)} file(s) uploaded and analyzed")

#         for file in uploaded_files:
#             info = detected_info[file.name]
#             with st.expander(
#                 f"📄 {file.name} - Detected as: **{info['type']}**", expanded=False
#             ):
#                 col1, col2, col3 = st.columns(3)
#                 with col1:
#                     st.metric("File Type", info["type"].upper())
#                 with col2:
#                     st.metric("Separator", f"'{info['separator']}'")
#                 with col3:
#                     st.metric("Size", f"{file.size:,} bytes")

#                 if info["suggestions"]:
#                     st.write("**Auto-detected mappings:**")
#                     for orig, mapped in info["suggestions"].items():
#                         st.code(f"{orig} → {mapped}")

#         if st.button("Continue to Header Mapping →", type="primary"):
#             st.rerun()


# def step_2_header_mapping() -> None:
#     """Step 2: Header mapping with auto-suggestions."""
#     st.header("🏷️ Map Column Headers", divider=True)

#     files = st.session_state.upload_workflow["files"]
#     separators = st.session_state.upload_workflow["detected_separators"]
#     auto_suggestions = st.session_state.upload_workflow["auto_suggestions"]
#     mappings = {}

#     st.info("📋 Review and adjust column mappings (auto-detected suggestions applied)")

#     for i, file in enumerate(files):
#         with st.expander(f"📄 {file.name}", expanded=True):
#             separator = separators.get(file.name, ",")
#             suggestions = auto_suggestions.get(file.name, {})

#             # Read sample with detected separator
#             sample_df = read_file_sample(file, separator)

#             if sample_df is not None:
#                 st.write("**Detected columns:**")
#                 cols = list(sample_df.columns)
#                 st.code(f"Separator: '{separator}' | Columns: {len(cols)}")

#                 # Enhanced standard fields based on sample data
#                 standard_fields = [
#                     "Select field...",
#                     # Common IDs
#                     "retailer_id",
#                     "transaction_id",
#                     "organization_id",
#                     "outlet_id",
#                     # Names
#                     "retailer_name",
#                     "organization_name",
#                     "outlet_name",
#                     "product_name",
#                     # Contact & Location
#                     "contact_info",
#                     "phone",
#                     "email",
#                     "address",
#                     "province",
#                     "city",
#                     "district",
#                     # Transaction fields
#                     "transaction_date",
#                     "amount",
#                     "quantity",
#                     "status",
#                     # Product fields
#                     "product_code",
#                     "product_category",
#                     "price",
#                     "discount",
#                     # Visit fields
#                     "visit_date",
#                     "dse_name",
#                     "visit_status",
#                     # Transfer fields
#                     "from_retailer",
#                     "to_retailer",
#                     "transfer_amount",
#                     # Other
#                     "other",
#                 ]

#                 file_mappings = {}
#                 col1, col2 = st.columns(2)

#                 for j, col in enumerate(cols):
#                     with col1 if j % 2 == 0 else col2:
#                         # Auto-select based on suggestions
#                         default_idx = 0
#                         suggested_field = suggestions.get(col, "")
#                         if suggested_field and suggested_field in standard_fields:
#                             default_idx = standard_fields.index(suggested_field)

#                         mapped_field = st.selectbox(
#                             f"`{col}` →",
#                             standard_fields,
#                             index=default_idx,
#                             key=f"mapping_{i}_{j}",
#                             help=f"Map column '{col}' to standard field",
#                         )
#                         if mapped_field != "Select field...":
#                             file_mappings[col] = mapped_field

#                 mappings[file.name] = file_mappings

#                 # Show sample data with current separator
#                 st.write("**Sample data preview:**")
#                 st.dataframe(sample_df.head(3), use_container_width=True)
#             else:
#                 st.error(f"❌ Could not read {file.name}")

#     # Save mappings to session state
#     st.session_state.upload_workflow["header_mappings"] = mappings

#     # Navigation buttons
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("← Back to Upload"):
#             st.session_state.upload_workflow["current_step"] = "upload"
#             st.rerun()

#     with col2:
#         # Check if at least one file has mappings
#         has_mappings = any(mappings.values())
#         if has_mappings:
#             if st.button("Continue to File Type →", type="primary"):
#                 st.session_state.upload_workflow["current_step"] = "file_type"
#                 st.rerun()
#         else:
#             st.button(
#                 "Continue to File Type →",
#                 disabled=True,
#                 help="Please map at least one column",
#             )


# def step_3_file_type() -> None:
#     """Step 3: File type selection with auto-detected suggestions."""
#     st.header("📊 Confirm Data Types", divider=True)

#     files = st.session_state.upload_workflow["files"]

#     st.info("🎯 Review auto-detected data types and adjust if needed")

#     # Get auto-detected types
#     file_types = {}
#     for file in files:
#         file_type, _, _ = detect_file_type_and_separator(file)
#         file_types[file.name] = file_type

#     # Data type options
#     data_type_options = [
#         ("retailer", "🏪 Retailer/Organization Data", "Store info, outlets, locations"),
#         (
#             "sellin",
#             "📦 Sell-in/Distribution Data",
#             "Stock distribution, product movement",
#         ),
#         (
#             "transaction",
#             "💰 Transaction Data",
#             "Sales transactions, customer purchases",
#         ),
#         ("transfer", "🔄 Transfer Data", "Balance transfers, fund movements"),
#         ("visit", "👥 Visit Data", "DSE visits, outlet interactions"),
#         ("other", "📄 Other Data", "Custom data type"),
#     ]

#     # Show file type selection for each file
#     for file in files:
#         with st.expander(
#             f"📄 {file.name} - Auto-detected: **{file_types[file.name]}**",
#             expanded=True,
#         ):
#             selected_type = st.radio(
#                 f"Data type for {file.name}:",
#                 options=[dt[0] for dt in data_type_options],
#                 index=next(
#                     i
#                     for i, dt in enumerate(data_type_options)
#                     if dt[0] == file_types[file.name]
#                 ),
#                 format_func=lambda x: next(
#                     dt[1] for dt in data_type_options if dt[0] == x
#                 ),
#                 key=f"type_{file.name}",
#                 help="This determines validation rules and database schema",
#             )
#             file_types[file.name] = selected_type

#             # Show description
#             description = next(
#                 dt[2] for dt in data_type_options if dt[0] == selected_type
#             )
#             st.caption(f"ℹ️ {description}")

#     # Save selections
#     st.session_state.upload_workflow["file_type"] = file_types

#     # Navigation buttons
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("← Back to Headers"):
#             st.session_state.upload_workflow["current_step"] = "headers"
#             st.rerun()

#     with col2:
#         if st.button("Continue to Preview →", type="primary"):
#             st.session_state.upload_workflow["current_step"] = "preview"
#             st.rerun()


# def step_4_preview() -> None:
#     """Step 4: Preview with proper parsing."""
#     st.header("👀 Preview & Validate", divider=True)

#     workflow = st.session_state.upload_workflow
#     files = workflow["files"]
#     mappings = workflow["header_mappings"]
#     file_types = workflow["file_type"]
#     separators = workflow["detected_separators"]

#     st.info("📋 Preview processed data before saving to database")

#     # Preview each file
#     preview_data = {}
#     for file in files:
#         file_type = file_types.get(file.name, "other")
#         separator = separators.get(file.name, ",")

#         with st.expander(f"📄 {file.name} ({file_type.upper()})", expanded=True):
#             df = read_file_sample(file, separator)

#             if df is not None:
#                 # Apply header mappings
#                 file_mappings = mappings.get(file.name, {})
#                 if file_mappings:
#                     df_mapped = df.rename(columns=file_mappings)
#                     st.write("**Mapped columns preview:**")
#                     st.dataframe(df_mapped, use_container_width=True)
#                     preview_data[file.name] = df_mapped
#                 else:
#                     st.write("**Original columns preview:**")
#                     st.dataframe(df, use_container_width=True)
#                     preview_data[file.name] = df

#                 # Show file stats
#                 col1, col2, col3, col4 = st.columns(4)
#                 with col1:
#                     st.metric("Rows (sample)", len(df))
#                 with col2:
#                     st.metric("Columns", len(df.columns))
#                 with col3:
#                     st.metric("File Size", f"{file.size:,} bytes")
#                 with col4:
#                     st.metric("Separator", f"'{separator}'")
#             else:
#                 st.error(f"❌ Could not preview {file.name}")

#     # Save preview data
#     st.session_state.upload_workflow["preview_data"] = preview_data

#     # Validation options
#     st.divider()
#     col1, col2 = st.columns(2)
#     with col1:
#         skip_duplicates = st.checkbox("Skip duplicate rows", value=True)
#     with col2:
#         validate_required = st.checkbox("Validate required fields", value=True)

#     # Navigation buttons
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         if st.button("← Back to File Type"):
#             st.session_state.upload_workflow["current_step"] = "file_type"
#             st.rerun()

#     with col2:
#         if st.button("🔄 Process Files", type="primary"):
#             st.session_state.upload_workflow["current_step"] = "process"
#             st.rerun()

#     with col3:
#         if st.button("🗑️ Reset All", help="Start over"):
#             reset_workflow()
#             st.rerun()


# def step_5_process() -> None:
#     """Step 5: Process with file-type specific logic."""
#     st.header("⚙️ Processing Files", divider=True)

#     workflow = st.session_state.upload_workflow
#     files = workflow["files"]
#     file_types = workflow["file_type"]
#     separators = workflow["detected_separators"]

#     # Process each file with type-specific logic
#     with st.spinner(f"Processing {len(files)} file(s)..."):
#         progress_bar = st.progress(0)

#         for i, file in enumerate(files):
#             file_type = file_types.get(file.name, "other")
#             separator = separators.get(file.name, ",")

#             st.write(f"Processing {file.name} as **{file_type}** data...")

#             # TODO: Implement type-specific ETL logic
#             # TODO: Save to appropriate SQLite tables based on file_type
#             # - retailer → retailers table
#             # - sellin → sellin_transactions table
#             # - transaction → transactions table
#             # - transfer → transfers table
#             # - visit → visits table

#             progress_bar.progress((i + 1) / len(files))

#         st.success(f"✅ Successfully processed {len(files)} file(s)")

#     # Show results summary
#     st.balloons()

#     # Results breakdown
#     with st.expander("📊 Processing Summary", expanded=True):
#         for file in files:
#             file_type = file_types.get(file.name, "other")
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 st.write(f"**{file.name}**")
#             with col2:
#                 st.write(f"Type: {file_type}")
#             with col3:
#                 st.write("✅ Processed")

#     # Final actions
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("🔄 Process More Files"):
#             reset_workflow()
#             st.rerun()

#     with col2:
#         if st.button("📊 View Dashboard", help="Go to data visualization"):
#             st.info("Dashboard navigation coming soon...")


# def main() -> None:
#     """Main function to orchestrate the upload workflow."""
#     init_session_state()

#     workflow = st.session_state.upload_workflow
#     current_step = workflow["current_step"]

#     # Step indicator
#     steps = ["upload", "headers", "file_type", "preview", "process"]
#     step_names = ["📁 Upload", "🏷️ Headers", "📊 Type", "👀 Preview", "⚙️ Process"]

#     # Show progress
#     st.markdown("**Progress:**")
#     cols = st.columns(5)
#     for i, (step, name) in enumerate(zip(steps, step_names, strict=False)):
#         with cols[i]:
#             if step == current_step:
#                 st.markdown(f"**{name}** ✅")
#             elif steps.index(current_step) > i:
#                 st.markdown(f"~~{name}~~ ✅")
#             else:
#                 st.markdown(f"{name}")

#     st.divider()

#     # Route to appropriate step
#     match current_step:
#         case "upload":
#             step_1_upload()
#         case "headers":
#             step_2_header_mapping()
#         case "file_type":
#             step_3_file_type()
#         case "preview":
#             step_4_preview()
#         case "process":
#             step_5_process()
#         case _:
#             st.error(f"Unknown step: {current_step}")
#             reset_workflow()


# if __name__ == "__main__":
#     main()
