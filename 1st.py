
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


geolocator = Nominatim(user_agent="mayur_travel_service")

try:
    start = input("Enter the first city: ")
    location1 = geolocator.geocode(start)
        
    destination= input("Enter the second city: ")
    location2 = geolocator.geocode(destination)

    if not location1 or not location2:
        print("Error: One or both cities could not be found.")
    else:
           coords1 = (location1.latitude, location1.longitude)
           coords2 = (location2.latitude, location2.longitude)

           distance = geodesic(coords1, coords2).kilometers
           mode={"rented car":[10 ,60 ,distance/60],
                "bus":[5 ,50 ,distance/50],
                "personal car":[1 ,70,distance/70],
                "train":[3 ,100 ,distance/100]}
           print("-"*30)
           print(f"The total travel distance is {distance:.3f} km\n")
           print("Follow is the rate table for various modes")
           print()
           print("   Vehicles           Rate(rs/km)         Speed(km/hr)          Time(hrs)       Total travel cost(rs)")
           for i,j in mode.items():
              print(f".  {i:15}    {j[0]:.3f}                 {j[1]:.3f}               {j[2]:.3f}             {(j[0]*distance):.3f}")

           ChoiceMode=(input("\nSelect the mode of travel :- \n  1.Rented Car\n  2.Bus\n  3.Personal Car\n  4.Train\n   "))  
           ChoiceMode=ChoiceMode.lower()
           match ChoiceMode:
                case "rented car":
                     print("Great you are going through a Rented Car")
                case "bus":
                     print("Great you are going through a Bus")        
                case "personal car":
                     print("Great you are going through a Personal Car") 
                case "train":
                     print("Great you are going through a Train")            
                case _:
                     print("Entered wrong mode choice")
                
           ChoiceStay=(input("Are you going to stay for more than a day, yes or no ?\n Ans:- ")).lower()
           match ChoiceStay:
                case "yes":
                     print(f"Great, you are going to stay at {destination}")

                case "no":
                     print(f"Great, you are going to return back same day from {destination}")
                case _:
                     print("Answer in yes or no")    
except Exception as e:
        print(f"An error occurred: {e}")



