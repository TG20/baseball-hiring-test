"""Main script for generating output.csv."""
import pandas as pd


def main():
    #import data"
    raw_data = pd.read_csv("././data/raw/pitchdata.csv")
    
    #AVG = (H / AB)
    def stat_avg(df):
        return round((df["H"] / df["AB"]),3)
        
    #OBP = (H + BB + HBP) / (AB + BB + HBP + SF)
    def stat_obp(df):
        return round(((df["H"] + df["BB"] + df["HBP"]) / (df["AB"] + df["BB"] + df["HBP"] + df["SF"])),3)

    #SLG = (TB / AB)
    def stat_slg(df):
        return round((df["TB"] / df["AB"]),3)

    #OPS = OBP + SLG
    def stat_ops(df):
        return round((stat_obp(df) + stat_slg(df)),3)

    def query_data(df):
        features = ["PA","AB","H","TB","BB","SF","HBP"]
        #groups pitcherside and hitterside for the pitcher team
        pitcher = df.groupby(["PitcherTeamId", "HitterSide"], as_index=False)[features].agg("sum")
        #print(pitcher)

        #adds PitcherTeamId to the SubjectId columnn
        #https://stackoverflow.com/a/39408701 
        pitcher.columns = ["SubjectId" if t == "PitcherTeamId" else t for t in pitcher.columns]
        pitcher["Split"] = pitcher["HitterSide"].apply(lambda t: "vs LHH" if t == "L" else "vs RHH")
        pitcher["Subject"] = "PitcherTeamId"
        
        #groups hitterside and pitcherside for the hitting team
        hitter = df.groupby(["HitterTeamId", "PitcherSide"], as_index=False)[features].agg("sum")
        
        #adds HitterTeamId to the SubjectId columnn
        hitter.columns = ["SubjectId" if t == "HitterTeamId" else t for t in hitter.columns]
        hitter["Split"] = hitter["PitcherSide"].apply(lambda t: "vs LHP" if t == "L" else "vs RHP")
        hitter["Subject"] = "HitterTeamId"
        
        #combine dataframes and only include PA subjects over 25
        updated_features = ["SubjectId","Split","Subject","PA","AB","H","TB","BB","SF","HBP"]
        combine_data = pitcher[updated_features].append(hitter[updated_features]) 
        filter_data = combine_data[combine_data["PA"]>=25]
        return filter_data
        
    #calculating stats
    data = query_data(raw_data)
    data["AVG"] = data.apply(stat_avg, axis=1)
    data["OBP"] = data.apply(stat_obp, axis=1)
    data["SLG"] = data.apply(stat_slg, axis=1)
    data["OPS"] = data.apply(stat_ops, axis=1)

    #reshape the data into a long format
    data = data.melt(id_vars=["SubjectId", "Split", "Subject"], value_vars=["AVG", "OBP", "SLG", "OPS"], var_name="Stat", value_name="Value")
    
    #export data
    data = data.sort_values(by=["SubjectId", "Stat", "Split", "Subject"], ascending=True)
    data[["SubjectId", "Stat", "Split", "Subject", "Value"]].to_csv("./data/processed/output.csv", index=False)

if __name__ == "__main__":
    main()
