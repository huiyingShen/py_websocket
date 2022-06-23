s = " ::ffff:50.202.230.43 - /9j/4AAQSkZJRgABAQAASABIAAD/4QBYRXhpZgAATU0AKgAAAAgAAgESAAM"
pos = s.find(" - ")
print(pos)
print(s[pos+3:])