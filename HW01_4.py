import pandas as pd
import numpy as np


def validate_and_clean_data(df):
    """
    Validates and separates complete and incomplete entries in the dataset.

    Parameters:
    - df (DataFrame): The input data.

    Returns:
    - complete_df (DataFrame): Entries with complete data (Date, Category, Amount).
    - incomplete_df (DataFrame): Entries with any missing or malformed data.
    """
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    complete_df = df.dropna(subset=['Date', 'Category', 'Amount'])
    incomplete_df = df[df.isnull().any(axis=1)].reset_index(drop=True)
    return complete_df, incomplete_df


def filter_by_date(df, start_date, end_date):
    mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
    return df[mask]


def display_results(complete_df, incomplete_df, summary):
    print("\n" + "=" * 50)
    print("Welcome to the Expense Tracker!")
    print("=" * 50 + "\n")

    if not incomplete_df.empty:
        print("Incomplete Entries:")
        print(incomplete_df.to_string(index=False))
    else:
        print("No incomplete entries found.")

    print("\n" + "=" * 50)
    print("Expense Summary:")
    print("=" * 50)

    if not summary.empty:
        print(summary)
        print(f"\nTotal Expense: {summary.sum():.2f}")
    else:
        print("No expenses found for the specified range.")
    print("=" * 50)


def edit_incomplete_entries(incomplete_df, file_path):
    while True:
        print("\nIncomplete Entries:\n")
        print(incomplete_df.reset_index(drop=False)
              .rename(columns={"index": "Row"})
              .to_string(index=False, header=True, na_rep="None"))
        print("\n1. Edit an entry (Column, Row)")
        print("2. Quit (q)")
        choice = input("\nEnter here: ").strip()

        if choice.lower() == 'q':
            break

        try:
            column, row = choice.split(",")
            column = column.strip()
            row = int(row.strip())

            if column not in incomplete_df.columns or row not in incomplete_df.index:
                print("Invalid selection. Please try again.")
                continue

            current_value = incomplete_df.at[row, column]
            new_value = input(f"Current value for {column} at row {row}: {current_value}\nEnter new value: ").strip()

            # Update the value in the DataFrame
            incomplete_df.at[row, column] = new_value

            # Update the original file
            df = pd.read_json(file_path) if file_path.endswith('.json') else pd.read_csv(file_path)
            df.loc[df.index[row], column] = new_value
            if file_path.endswith('.json'):
                df.to_json(file_path, orient='columns', date_format='iso')
            elif file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
            print(f"\n[{file_path}] edit complete.\n")
        except Exception as e:
            print(f"Error: {e}. Please ensure input is in the format 'Column, Row'.")


def expense_tracker():
    file_path = input("Enter the file path (CSV/JSON): ").strip()
    try:
        if file_path.endswith('.json'):
            df = pd.read_json(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            raise ValueError("Unsupported file format. Please provide a CSV or JSON file.")

        while True:
            complete_df, incomplete_df = validate_and_clean_data(df)

            print("\nSelect a time range:")
            print("1. Last week")
            print("2. Last month")
            print("3. Custom range")
            choice = input("Enter your choice (1/2/3): ").strip()

            if choice == '1':
                end_date = pd.Timestamp.today()
                start_date = end_date - pd.Timedelta(weeks=1)
            elif choice == '2':
                end_date = pd.Timestamp.today()
                start_date = end_date - pd.DateOffset(months=1)
            elif choice == '3':
                start_date = input("Enter start date (YYYY-MM-DD): ").strip()
                end_date = input("Enter end date (YYYY-MM-DD): ").strip()
                pd.to_datetime(start_date)
                pd.to_datetime(end_date)
            else:
                raise ValueError("Invalid choice. Please enter 1, 2, or 3.")

            filtered_df = filter_by_date(complete_df, start_date, end_date)
            summary = filtered_df.groupby('Category')['Amount'].sum()
            display_results(filtered_df, incomplete_df, summary)

            print("\nSelect a choice:")
            print("1. Reselect time range")
            print("2. Fill out incomplete entries")
            print("q. Quit")
            next_choice = input("Enter your choice (1/2/q): ").strip()

            if next_choice == '1':
                continue
            elif next_choice == '2':
                edit_incomplete_entries(incomplete_df, file_path)
            elif next_choice.lower() == 'q':
                print("Thank you for using the Expense Tracker. Goodbye!")
                break
            else:
                print("Invalid choice. Exiting program.")
                break
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Run the program
expense_tracker()
