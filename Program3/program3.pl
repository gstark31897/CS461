% run main when prlog loads this (makes it easier to test)
:- initialization(main).

% nephews are named huey, louie and dewey
valid_name(Name) :- member(Name, [huey, louie, dewey]).

% nephews are ages 4, 5 and 6
valid_age(Age) :- member(Age, [4, 5, 6]).

% nephews can wear, green, yellow, white
valid_color(Name, Color, Animal) :- Name\=dewey, Name\=huey, Color=green, member(Animal, [camel, giraffe, panda]). % huey is younger than the nephew wearing green
valid_color(Name, Color, Animal) :- Name=dewey, Color=yellow, member(Animal, [camel, giraffe, panda]). % dewey is wearing yellow
valid_color(Name, Color, Animal) :- Name\=dewey, Color=white, member(Animal, [camel, giraffe]). % the panda is not on the white shirt

valid_animal(Name, Age, Animal) :- Name=louie, Age\=5, Animal=giraffe. % louie has the giraffe
valid_animal(Name, Age, Animal) :- Name\=louie, Age=5, Animal=camel. % the 5 year old has the camel
valid_animal(Name, Age, Animal) :- Name\=louie, Age\=5, Animal=panda.

% a nephew must have a valid name, age, color and animal
nephew(Name, Age, Color, Animal) :- valid_name(Name), valid_age(Age), valid_color(Name, Color, Animal), valid_animal(Name, Age, Animal).

solutions(huey, A2, A3, A4, B1, B2, green, B4, C1, C2, C3, C4) :-
    nephew(huey, A2, A3, A4), nephew(B1, B2, green, B4), nephew(C1, C2, C3, C4), % there are 3 nephews
    A2 < B2, % huey is younger than the nephew with the green shirt
    C1\=huey, C3\=green, % the nephews all have different names and different color shirts
    C2\=A2, C2\=B2, % the nephews are all different ages
    A4\=B4, B4\=C4. % the nephews all have different animals on their shirts

% find and print every possible solution
main :- findall([A1, A2, A3, A4, B1, B2, B3, B4, C1, C2, C3, C4], (solutions(A1, A2, A3, A4, B1, B2, B3, B4, C1, C2, C3, C4), print([[A1, A2, A3, A4], [B1, B2, B3, B4], [C1, C2, C3, C4]]), nl), _), halt.

