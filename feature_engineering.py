import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
np.random.seed(42)

print("--> Generating automotive pricing dataset (500 records)...")
n_samples = 500

brands = np.random.choice(["Toyota", "Honda", "BMW", "Ford", "Hyundai"], size=n_samples)
vehicle_age = np.random.randint(1, 15, size=n_samples)
mileage = vehicle_age * np.random.normal(loc=12000, scale=3000, size=n_samples).astype(int)
mileage = np.clip(mileage, 2000, 200000)

base_prices = {"Toyota": 28000, "Honda": 27000, "BMW": 48000, "Ford": 30000, "Hyundai": 24000}
brand_base = np.array([base_prices[b] for b in brands])

price = brand_base - (vehicle_age * 1500) - (mileage * 0.08) + np.random.normal(0, 2500, n_samples)
price = np.clip(price, 3000, 85000).round(2)

df = pd.DataFrame({
    "Brand": brands,
    "Vehicle_Age_Years": vehicle_age,
    "Mileage_Miles": mileage,
    "Price_USD": price
})

df.to_csv("automotive_pricing_raw.csv", index=False)

print("--> Engineering new features...")

# Feature 1: Price per Mile (Price / Mileage)
df["Price_Per_Mile"] = (df["Price_USD"] / df["Mileage_Miles"]).round(4)

# Feature 2: Mileage per Year (Usage Intensity)
df["Mileage_Per_Year"] = (df["Mileage_Miles"] / df["Vehicle_Age_Years"]).round(2)

# Feature 3: Depreciation Rate Percentage per Year
df["Brand_Base_Price"] = df["Brand"].map(base_prices)
df["Depreciation_Rate_Pct"] = (((df["Brand_Base_Price"] - df["Price_USD"]) / df["Brand_Base_Price"]) / df["Vehicle_Age_Years"] * 100).round(2)

# Feature 4: Vehicle Segment Classification (Categorical One-Hot Encoding)
def assign_segment(row):
    if row["Price_USD"] > 35000:
        return "Luxury"
    elif row["Vehicle_Age_Years"] <= 3:
        return "Nearly New"
    else:
        return "Economy"

df["Vehicle_Segment"] = df.apply(assign_segment, axis=1)

df_encoded = pd.get_dummies(df, columns=["Vehicle_Segment"], drop_first=False)
df_encoded.to_csv("automotive_pricing_engineered.csv", index=False)

print("--> Generating feature correlation and visualization charts...")

# Chart 1: Price vs Vehicle Age with Segment Hue
plt.figure(figsize=(8, 5))
sns.scatterplot(data=df, x="Vehicle_Age_Years", y="Price_USD", hue="Vehicle_Segment", palette="Set1", alpha=0.8)
plt.title("Vehicle Price vs. Age by Segment")
plt.xlabel("Vehicle Age (Years)")
plt.ylabel("Price (USD)")
plt.tight_layout()
plt.savefig("fig1_price_vs_age.png", dpi=300)
plt.close()

# Chart 2: Depreciation Rate by Brand (Boxplot)
plt.figure(figsize=(8, 5))
sns.boxplot(data=df, x="Brand", y="Depreciation_Rate_Pct", palette="Pastel1")
plt.title("Annual Depreciation Rate (%) Distribution Across Brands")
plt.xlabel("Brand")
plt.ylabel("Depreciation Rate (% / Year)")
plt.tight_layout()
plt.savefig("fig2_depreciation_by_brand.png", dpi=300)
plt.close()

# Chart 3: Mileage Per Year vs Price Per Mile (Feature Interaction)
plt.figure(figsize=(8, 5))
sns.scatterplot(data=df, x="Mileage_Per_Year", y="Price_Per_Mile", hue="Brand", alpha=0.7)
plt.title("Usage Intensity (Mileage/Yr) vs. Price Per Mile")
plt.xlabel("Mileage Per Year (Miles/Yr)")
plt.ylabel("Price Per Mile ($/Mile)")
plt.tight_layout()
plt.savefig("fig3_usage_vs_price_per_mile.png", dpi=300)
plt.close()

# Chart 4: Feature Correlation Heatmap
plt.figure(figsize=(8, 6))
numeric_cols = ["Vehicle_Age_Years", "Mileage_Miles", "Price_USD", "Price_Per_Mile", "Mileage_Per_Year", "Depreciation_Rate_Pct"]
corr_matrix = df[numeric_cols].corr()
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Correlation Matrix: Raw vs. Engineered Features")
plt.tight_layout()
plt.savefig("fig4_correlation_heatmap.png", dpi=300)
plt.close()

print("All features engineered and 4 charts successfully generated!")