from flask import Flask, render_template, request
import math
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 获取用户输入的数据，并进行清理
        depth_range = float(request.form.get('depth_range', 0).strip())
        area_range = float(request.form.get('area_range', 0).strip())
        surface_temperature = float(request.form.get('surface_temperature', 0).strip())
        rock_heat_generation = float(request.form.get('rock_heat_generation', 0).strip())
        geothermal_flux = float(request.form.get('geothermal_flux', 0).strip())
        thermal_conductivity = float(request.form.get('thermal_conductivity', 0).strip())
        depth1 = float(request.form.get('depth1', 0).strip())
        depth2 = float(request.form.get('depth2', 0).strip())
        year = int(request.form.get('year', 0).strip())
        # 获取地热发电数据
        fluid_density = 1078
        fluid_specific_heat = 4250
        average_capacity_factor = 0.9
        fluid_flow_rate = {2025: 60, 2030: 70, 2035: 85, 2040: 100, 2045: 100, 2050: 100}
        annual_operating_hours = 8760

        # 获取财务指标数据
        drilling_cost_coefficients = {2025: 0.95, 2030: 0.9, 2035: 0.85, 2040: 0.8, 2045: 0.75, 2050: 0.7}
        c_extra = 1
        learning_factor = 0.87
        capital_recovery_factor = 0.08

        # 计算深度温度和热储量
        depth_temperature1 = surface_temperature + (geothermal_flux * depth1 / thermal_conductivity) - \
                             (rock_heat_generation * (depth1 ** 2) / (2 * thermal_conductivity))
        depth_temperature2 = surface_temperature + (geothermal_flux * depth2 / thermal_conductivity) - \
                             (rock_heat_generation * (depth2 ** 2) / (2 * thermal_conductivity))
        heat_storage = 2550 * 1 * area_range * ((depth_temperature1 + depth_temperature2) / 2 - surface_temperature) * \
                       depth_range * 1e-18

        # 计算净热效率、年发电量和装机容量
        net_thermal_efficiency = 0.00052 * (depth_temperature2 + 18) / 2 + 0.032
        annual_power_generation = fluid_flow_rate[year] * fluid_density * fluid_specific_heat * \
                                  (depth_temperature2 - 18) * net_thermal_efficiency * 1e-3 * annual_operating_hours * \
                                  average_capacity_factor / 1e9
        installed_capacity = annual_power_generation / (average_capacity_factor * annual_operating_hours) * 1000


        # 计算钻井成本、地表发电成本、储层增产成本等
        drilling_cost = \
                    (1.72 * 1e-7 * 1 + 2.3e-3 + 0.62 * (geothermal_flux / (thermal_conductivity * depth_temperature2)) \
                     * drilling_cost_coefficients[year]) * depth2
        surface_power_cost = 750 + 1125 * (math.exp(-0.006115 * (installed_capacity - 5)))
        reservoir_stimulation_cost = 2.5
        geothermal_distribution_cost = 50 * installed_capacity/1000
        exploration_cost = 1.12 * (c_extra + 0.6 * drilling_cost)
        capex = (drilling_cost * 2 + surface_power_cost * installed_capacity / 1e3 + reservoir_stimulation_cost + \
                 geothermal_distribution_cost + exploration_cost) * learning_factor
        lcoe = (capex * 0.08+ capex * 0.02) * 1e3 / annual_power_generation

        # 渲染结果页面
        return render_template('result.html',
                               depth_temperature2=depth_temperature2,
                               heat_storage=heat_storage,
                               net_thermal_efficiency=net_thermal_efficiency,
                               annual_power_generation=annual_power_generation,
                               installed_capacity=installed_capacity,
                               drilling_cost=drilling_cost,
                               surface_power_cost=surface_power_cost,
                               reservoir_stimulation_cost=reservoir_stimulation_cost,
                               geothermal_distribution_cost=geothermal_distribution_cost,
                               exploration_cost=exploration_cost,
                               capex=capex,
                               lcoe=lcoe)
    else:
        # 渲染输入页面
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)



