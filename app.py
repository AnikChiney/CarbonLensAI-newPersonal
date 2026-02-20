from flask import Flask, render_template, request
import json

app = Flask(__name__)

# Carbon pricing by country (USD per tonne CO2)
CARBON_PRICING = {
    'default': 50,
    'canada': 65,
    'united kingdom': 85,
    'germany': 90,
    'france': 95,
    'sweden': 130,
    'switzerland': 120,
    'norway': 80,
    'united states': 45,
    'china': 15,
    'india': 10,
    'australia': 55,
    'japan': 40,
    'south korea': 25,
    'brazil': 12,
    'mexico': 18,
    'south africa': 20
}

# Country average emissions (tonnes CO2 per capita)
COUNTRY_AVERAGES = {
    'default': 4.5,
    'united states': 14.2,
    'canada': 15.4,
    'australia': 15.0,
    'saudi arabia': 16.9,
    'russia': 11.8,
    'japan': 8.6,
    'germany': 7.9,
    'china': 7.6,
    'united kingdom': 5.2,
    'france': 4.6,
    'india': 1.9,
    'brazil': 2.0,
    'mexico': 3.0,
    'south africa': 7.4,
    'indonesia': 2.3,
    'argentina': 3.9,
    'turkey': 5.1,
    'pakistan': 0.9,
    'bangladesh': 0.6,
    'nigeria': 0.6,
    'egypt': 2.5,
    'vietnam': 3.5,
    'philippines': 1.2,
    'thailand': 3.8,
    'malaysia': 8.0,
    'singapore': 8.9,
    'south korea': 11.8,
    'italy': 5.4,
    'spain': 5.0,
    'netherlands': 8.1,
    'sweden': 3.4,
    'norway': 7.6,
    'switzerland': 4.1,
    'austria': 6.9,
    'belgium': 8.0,
    'denmark': 5.0,
    'finland': 7.9,
    'ireland': 7.7,
    'new zealand': 6.8,
    'israel': 6.2,
    'chile': 4.4,
    'peru': 1.7,
    'colombia': 1.8,
    'morocco': 1.7,
    'kenya': 0.4,
    'ethiopia': 0.1,
    'ghana': 0.5,
    'tanzania': 0.2,
    'uganda': 0.1,
    'zambia': 0.3,
    'zimbabwe': 0.7,
    'botswana': 2.6,
    'namibia': 1.5,
    'myanmar': 0.6,
    'sri lanka': 0.8,
    'nepal': 0.3,
    'cambodia': 0.9,
    'laos': 2.6,
    'mongolia': 11.1,
    'uzbekistan': 3.2,
    'kazakhstan': 13.0,
    'ukraine': 5.0,
    'poland': 7.8,
    'czech republic': 9.0,
    'romania': 3.7,
    'hungary': 4.4,
    'portugal': 4.0,
    'greece': 5.7,
    'croatia': 4.2,
    'serbia': 6.0,
    'bulgaria': 6.8,
    'slovakia': 6.0,
    'slovenia': 6.0,
    'lithuania': 3.5,
    'latvia': 3.3,
    'estonia': 7.8,
    'cyprus': 5.6,
    'luxembourg': 15.3,
    'malta': 3.0,
    'iceland': 9.9,
    'liechtenstein': 3.8,
    'monaco': 2.5,
    'andorra': 6.0,
    'san marino': 5.5,
    'vatican city': 0.5
}

# Flight emission factors (kg CO2 per passenger km)
FLIGHT_EMISSION_FACTORS = {
    'economy': 0.255,
    'business': 0.510,
    'first': 0.765
}

# Carbon credit pricing (USD per tonne)
CARBON_CREDIT_PRICING = {
    'forestry': 15,
    'renewable': 20,
    'cookstove': 12,
    'methane': 18,
    'direct_air': 120,
    'premium': 50
}

def calculate_emissions(data):
    """Calculate carbon emissions based on user inputs"""
    country = data.get('country', '').lower().strip()
    distance = float(data.get('distance', 0))
    electricity = float(data.get('electricity', 0))
    meals = float(data.get('meals', 3))
    waste = float(data.get('waste', 0))
    renewable = float(data.get('renewable', 0))
    reduction = float(data.get('reduction', 10))
    
    flight_distance = float(data.get('flight_distance', 0))
    flight_class = data.get('flight_class', 'economy')
    
    country_avg = COUNTRY_AVERAGES.get(country, COUNTRY_AVERAGES['default'])
    
    transport_emissions = (distance * 0.12 * 365) / 1000
    electricity_factor = 0.4 * (1 - renewable / 100)
    electricity_emissions = (electricity * electricity_factor * 12) / 1000
    food_emissions = (meals * 2.5 * 365) / 1000
    waste_emissions = (waste * 0.5 * 52) / 1000
    
    flight_factor = FLIGHT_EMISSION_FACTORS.get(flight_class, 0.255)
    flight_emissions = (flight_distance * flight_factor * 2) / 1000
    
    personal_current = transport_emissions + electricity_emissions + food_emissions + waste_emissions + flight_emissions
    flight_percentage = (flight_emissions / personal_current * 100) if personal_current > 0 else 0
    
    if personal_current > country_avg * 1.3:
        risk = "High"
    elif personal_current > country_avg * 0.9:
        risk = "Medium"
    else:
        risk = "Low"
    
    years = list(range(2025, 2035))
    original = [personal_current * (1.02 ** i) for i in range(10)]
    adjusted = [personal_current * (1 - reduction/100) * (0.98 ** i) for i in range(10)]
    
    breakdown = {
        'Transport': round(transport_emissions, 2),
        'Electricity': round(electricity_emissions, 2),
        'Food': round(food_emissions, 2),
        'Waste': round(waste_emissions, 2),
        'Flights': round(flight_emissions, 2)
    }
    
    cost_analysis = calculate_cost_analysis(
        country, personal_current, transport_emissions, 
        electricity_emissions, food_emissions, waste_emissions,
        flight_emissions, reduction, renewable
    )
    
    carbon_credit_analysis = calculate_carbon_credits(
        flight_emissions, personal_current, country
    )
    
    recommendations = generate_recommendations(
        transport_emissions, electricity_emissions, food_emissions, 
        waste_emissions, flight_emissions, renewable, reduction,
        flight_distance, flight_class
    )
    
    return {
        'personal_current': round(personal_current, 2),
        'country_avg': country_avg,
        'risk': risk,
        'years': years,
        'original': [round(x, 2) for x in original],
        'adjusted': [round(x, 2) for x in adjusted],
        'breakdown': breakdown,
        'reduction_scenario': reduction,
        'cost_analysis': cost_analysis,
        'carbon_credit_analysis': carbon_credit_analysis,
        'recommendations': recommendations,
        'flight_data': {
            'distance': flight_distance,
            'class': flight_class,
            'emissions': round(flight_emissions, 2),
            'percentage': round(flight_percentage, 1),
            'per_km': flight_factor
        }
    }

def calculate_cost_analysis(country, total_emissions, transport, electricity, food, waste, flights, reduction_target, renewable_pct):
    """Calculate cost implications including flight carbon costs"""
    carbon_price = CARBON_PRICING.get(country, CARBON_PRICING['default'])
    
    transport_cost = round(transport * carbon_price)
    electricity_cost = round(electricity * carbon_price)
    food_cost = round(food * carbon_price * 0.3)
    waste_cost = round(waste * carbon_price * 0.5)
    flight_cost = round(flights * carbon_price * 1.5)
    
    current_annual_cost = transport_cost + electricity_cost + food_cost + waste_cost + flight_cost
    
    flight_reduction_savings = round(flight_cost * 0.5)
    solar_savings = round(electricity_cost * 0.6)
    transport_savings = round(transport_cost * 0.35)
    efficiency_savings = round(electricity_cost * 0.25)
    
    potential_savings = solar_savings + transport_savings + efficiency_savings + flight_reduction_savings
    
    ten_year_savings = potential_savings * 10
    ten_year_reduction = (potential_savings / carbon_price) * 10
    
    scenarios = {
        'costs': [
            current_annual_cost,
            current_annual_cost - solar_savings,
            current_annual_cost - transport_savings,
            current_annual_cost - efficiency_savings,
            current_annual_cost - flight_reduction_savings,
            current_annual_cost - potential_savings
        ],
        'carbon_costs': [
            current_annual_cost,
            round((total_emissions - electricity * 0.6) * carbon_price),
            round((total_emissions - transport * 0.35) * carbon_price),
            round((total_emissions - electricity * 0.25) * carbon_price),
            round((total_emissions - flights * 0.5) * carbon_price),
            round((total_emissions - (electricity * 0.6 + transport * 0.35 + electricity * 0.25 + flights * 0.5)) * carbon_price)
        ],
        'savings': [0, solar_savings, transport_savings, efficiency_savings, flight_reduction_savings, potential_savings],
        'labels': ['Current', 'With Solar', 'With EV', 'Efficiency', 'Reduce Flights', 'Full Plan']
    }
    
    return {
        'current_annual_cost': current_annual_cost,
        'transport_cost': transport_cost,
        'electricity_cost': electricity_cost,
        'food_cost': food_cost,
        'waste_cost': waste_cost,
        'flight_cost': flight_cost,
        'potential_savings': potential_savings,
        'solar_savings': solar_savings,
        'transport_savings': transport_savings,
        'efficiency_savings': efficiency_savings,
        'flight_reduction_savings': flight_reduction_savings,
        'ten_year_savings': ten_year_savings,
        'ten_year_reduction': round(ten_year_reduction, 1),
        'roi_scenarios': scenarios,
        'carbon_price': carbon_price
    }

def calculate_carbon_credits(flight_emissions, total_emissions, country):
    """Calculate carbon credit requirements and costs"""
    flight_credits_needed = round(flight_emissions, 2)
    total_credits_needed = round(total_emissions, 2)
    
    credit_costs = {}
    for credit_type, price in CARBON_CREDIT_PRICING.items():
        credit_costs[credit_type] = {
            'flight_only': round(flight_credits_needed * price * 85),  # Convert to INR (approx 85)
            'total_offset': round(total_credits_needed * price * 85),
            'price_per_tonne': price
        }
    
    trees_needed = int(flight_emissions * 45)
    renewable_kwh = int(flight_emissions * 1500)
    
    flight_equivalents = {
        'trees_to_offset': trees_needed,
        'solar_kwh_equivalent': renewable_kwh,
        'driving_km_equivalent': int(flight_emissions * 1000 / 0.12),
        'meals_equivalent': int(flight_emissions * 1000 / 2.5)
    }
    
    return {
        'flight_credits_needed': flight_credits_needed,
        'total_credits_needed': total_credits_needed,
        'credit_costs': credit_costs,
        'flight_equivalents': flight_equivalents,
        'recommended_project': 'forestry' if flight_emissions < 5 else 'renewable',
        'monthly_flight_cost': round(credit_costs['premium']['flight_only'] / 12)
    }

def generate_recommendations(transport, electricity, food, waste, flights, renewable_pct, reduction_target, flight_distance, flight_class):
    """Generate personalized recommendations including flight-specific"""
    recommendations = []
    
    emissions = {
        'transport': transport,
        'electricity': electricity,
        'food': food,
        'waste': waste,
        'flights': flights
    }
    sorted_emissions = sorted(emissions.items(), key=lambda x: x[1], reverse=True)
    
    if flights > 1.0:
        recommendations.append({
            'icon': 'fa-plane-slash',
            'title': 'Reduce Air Travel - Use Virtual Meetings',
            'description': f'Your flights emit {round(flights, 1)} tonnes CO₂ annually. Replace 50% of business travel with video conferencing to significantly reduce this.',
            'annual_savings': 800,
            'carbon_reduction': round(flights * 0.5, 1),
            'investment': 500,
            'payback_period': '1 month',
            'roi': 1600,
            'category': 'flight'
        })
        
        recommendations.append({
            'icon': 'fa-leaf',
            'title': 'Purchase Verified Carbon Credits for Flights',
            'description': 'Offset unavoidable flight emissions by purchasing Gold Standard certified credits. Cost-effective way to achieve carbon neutrality for air travel.',
            'annual_savings': 0,
            'carbon_reduction': round(flights, 1),
            'investment': round(flights * 50 * 85),
            'payback_period': 'Immediate impact',
            'roi': 0,
            'category': 'flight'
        })
        
        if flight_class in ['business', 'first']:
            recommendations.append({
                'icon': 'fa-chair',
                'title': f'Fly Economy Instead of {flight_class.title()}',
                'description': f'Switching from {flight_class} to economy reduces your flight emissions by 50-67% while saving money on ticket prices.',
                'annual_savings': 1200,
                'carbon_reduction': round(flights * 0.5, 1),
                'investment': 0,
                'payback_period': 'Immediate',
                'roi': 0,
                'category': 'flight'
            })
        
        recommendations.append({
            'icon': 'fa-train',
            'title': 'Choose Rail for Short-Haul Trips (<800km)',
            'description': 'For trips under 800km, trains emit 90% less CO₂ than flights. Consider high-speed rail for regional travel.',
            'annual_savings': 400,
            'carbon_reduction': round(flights * 0.3, 1),
            'investment': 0,
            'payback_period': 'Immediate',
            'roi': 0,
            'category': 'flight'
        })
    
    if transport > 1.0:
        recommendations.append({
            'icon': 'fa-bicycle',
            'title': 'Switch to Electric Vehicle or Public Transit',
            'description': 'Replace your gasoline vehicle with an EV or use public transit for your daily commute.',
            'annual_savings': 420,
            'carbon_reduction': round(transport * 0.35, 1),
            'investment': 35000,
            'payback_period': '7 years',
            'roi': 14,
            'category': 'transport'
        })
    
    if electricity > 1.5:
        recommendations.append({
            'icon': 'fa-solar-panel',
            'title': 'Install Rooftop Solar Panels',
            'description': 'Generate your own clean electricity with a 5kW solar system.',
            'annual_savings': 580,
            'carbon_reduction': round(electricity * 0.6, 1),
            'investment': 12000,
            'payback_period': '5-7 years',
            'roi': 18,
            'category': 'energy'
        })
        
        recommendations.append({
            'icon': 'fa-home',
            'title': 'Home Energy Efficiency Upgrade',
            'description': 'Install smart thermostats, LED lighting, and improve insulation.',
            'annual_savings': 240,
            'carbon_reduction': round(electricity * 0.25, 1),
            'investment': 2500,
            'payback_period': '10 months',
            'roi': 96,
            'category': 'energy'
        })
    
    if food > 2.0:
        recommendations.append({
            'icon': 'fa-carrot',
            'title': 'Adopt Plant-Based Diet 3 Days/Week',
            'description': 'Reducing meat consumption significantly lowers your food-related carbon footprint.',
            'annual_savings': 180,
            'carbon_reduction': round(food * 0.2, 1),
            'investment': 0,
            'payback_period': 'Immediate',
            'roi': 0,
            'category': 'food'
        })
    
    if waste > 0.5:
        recommendations.append({
            'icon': 'fa-recycle',
            'title': 'Zero Waste Lifestyle Program',
            'description': 'Implement composting, recycling, and buy-in-bulk strategies.',
            'annual_savings': 120,
            'carbon_reduction': round(waste * 0.4, 1),
            'investment': 150,
            'payback_period': '15 months',
            'roi': 80,
            'category': 'waste'
        })
    
    if renewable_pct < 20:
        recommendations.append({
            'icon': 'fa-wind',
            'title': 'Switch to Green Energy Provider',
            'description': 'Choose a utility company that offers 100% renewable energy plans.',
            'annual_savings': 200,
            'carbon_reduction': round(electricity * 0.5, 1),
            'investment': 0,
            'payback_period': 'Immediate',
            'roi': 0,
            'category': 'energy'
        })
    
    if transport > 0.8:
        recommendations.append({
            'icon': 'fa-laptop-house',
            'title': 'Negotiate Remote Work 2 Days/Week',
            'description': 'Working from home 2 days per week reduces commuting emissions by 40%.',
            'annual_savings': 340,
            'carbon_reduction': round(transport * 0.4, 1),
            'investment': 200,
            'payback_period': '3 weeks',
            'roi': 1700,
            'category': 'transport'
        })
    
    recommendations.sort(key=lambda x: (x['roi'] == 0, -x['roi']))
    return recommendations[:6]

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        result = calculate_emissions(request.form)
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)