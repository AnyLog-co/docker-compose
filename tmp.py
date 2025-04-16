output = ""
for i in ["a_current", "a_n_voltage", "b_current", "b_n_voltage", "c_current", "c_n_voltage"]:
	output += f"min({i}) as min_{i}, avg({i}) as avg_{i}, max({i}) as max_{i},"
print(output)
