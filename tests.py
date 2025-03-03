def main():
    dict1 = {"A": 1, "B": 2}
    dict2 = {"C": 3}
    dict2.update(dict1)
    print(f"{dict2}")
    
if __name__ == "__main__":
    main()