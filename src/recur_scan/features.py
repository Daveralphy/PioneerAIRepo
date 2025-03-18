from recur_scan.transactions import Transaction
import pandas as pd


def get_n_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> int:
    """Get the number of transactions in all_transactions with the same amount as transaction"""
    return len([t for t in all_transactions if t.amount == transaction.amount])

def get_percent_transactions_same_amount(transaction: Transaction, all_transactions: list[Transaction]) -> float:
    """Get the percentage of transactions in all_transactions with the same amount as transaction"""
    if not all_transactions:
        return 0.0
    n_same_amount = len([t for t in all_transactions if t.amount == transaction.amount])
    return n_same_amount / len(all_transactions)

def get_basic_features(transaction: Transaction, all_transactions: list[Transaction]) -> dict[str, float | int]:
    features = {
        "n_transactions_same_amount": get_n_transactions_same_amount(transaction, all_transactions),
        "percent_transactions_same_amount": get_percent_transactions_same_amount(transaction, all_transactions),
    }

    # New feature: check if amount ends in .99 and is between 0 to 50
    amount = transaction.amount
    features['amount_ends_in_99'] = (amount % 1 == 0.99) and (0 <= amount <= 50)

    # New feature: check if time between transactions is 14 days, 1 month, 6 months, or 1 year
    transaction_dates = [t.date for t in all_transactions]
    transaction_dates.sort()
    time_diffs = pd.Series(transaction_dates).diff().dt.days.dropna()

    features['time_diff_14_days'] = any(time_diffs == 14)
    features['time_diff_1_month'] = any(time_diffs.between(28, 31))
    features['time_diff_6_months'] = any(time_diffs.between(180, 183))
    features['time_diff_1_year'] = any(time_diffs.between(365, 366))

    # Additional features
    user_transactions = [t for t in all_transactions if t.user_id == transaction.user_id]
    features['transaction_frequency'] = len(user_transactions)
    features['average_transaction_amount'] = sum(t.amount for t in user_transactions) / len(user_transactions)
    features['transaction_amount_variance'] = pd.Series([t.amount for t in user_transactions]).var()
    features['time_since_last_transaction'] = (transaction.date - max(t.date for t in user_transactions if t.date < transaction.date)).days if len(user_transactions) > 1 else 0
    features['day_of_week'] = transaction.date.weekday()
    features['month_of_year'] = transaction.date.month
    features['is_weekend'] = transaction.date.weekday() >= 5
    recurring_amounts = [9.99, 19.99, 29.99, 39.99, 49.99]
    features['is_recurring_amount'] = amount in recurring_amounts

    return features