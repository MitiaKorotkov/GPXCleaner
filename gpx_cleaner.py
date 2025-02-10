import sys
from gpx_parser import read_gpx, write_to_gpx
from ml_tools import clean_df_target, add_features
from joblib import load



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Ошибка! Правильное шаблон команды: python3 gpx_cleaner.py <input_file> <output_file>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        
        print(f"input: {input_file}")
        df = read_gpx("", [input_file])
        df = add_features(df)

        features = ["arc_distances_from_start", "angles_betwen_segments", "lengths_betwen_segments", "dbscan_result", "angles_betwen_segments_5",
            "angles_betwen_segments_15", "angles_betwen_segments_25", "angles_betwen_segments_35", "angles_betwen_segments_45", "angles_betwen_segments_55", 
            "angles_betwen_segments_65", "angles_betwen_segments_75", "angles_betwen_segments_85", "angles_betwen_segments_95"]
        
        X = df[features].values
        model = load('models/RandomForestV1.pkl')

        df["model_label"] = model.predict(X)
        clean_df_target(df, target_column="model_label", window=2)

        clean_df = df[df['model_label'] == 0]
        write_to_gpx(clean_df, output_file)
