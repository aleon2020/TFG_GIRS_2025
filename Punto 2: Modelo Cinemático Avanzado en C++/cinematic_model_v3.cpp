// Implementación de un robot por cables para el control
// de un efector final en diversas tareas

#include <iostream>
#include <cmath>
#include <vector>
#include <map>
#include "matplotlibcpp.h"

namespace plt = matplotlibcpp;

// COMPILACIÓN, ENLAZADO Y EJECUCIÓN
// g++ cinematic_model_v3.cpp -o cinematic_model_v3 -I /usr/include/python3.12 -I $(python3 -c "import numpy; print(numpy.get_include())") -lpython3.12
// ./cinematic_model_v3

// PARÁMETROS
const double largo_plano = 100;
const double alto_plano = 100;
const double largo_efector = 10;
const double alto_efector = 10;
const double radio_rueda = 25;

// LÍMITES DE MOVIMIENTO
std::vector<std::string> 
verificar_limites(double x, double y) 
{
    std::vector<std::string> errores;
    if (x >= (largo_plano - (largo_efector / 2)) || x <= (largo_efector / 2)) {
        errores.push_back("FUERA DEL LÍMITE en x = " + std::to_string(x));
    }
    if (y >= (alto_plano - (alto_efector / 2)) || y <= (alto_efector / 2)) {
        errores.push_back("FUERA DEL LÍMITE en y = " + std::to_string(y));
    }
    return errores;
}

// EFECTOR FINAL
void 
calcular_esquinas(double x, double y,
                  double& x1, double& y1, double& x2, double& y2,
                  double& x3, double& y3, double& x4, double& y4)
{
    // Esquina superior izquierda (x1, y1)
    x1 = x - (largo_efector / 2);
    y1 = y + (alto_efector / 2);

    // Esquina superior derecha (x2, y2)
    x2 = x + (largo_efector / 2);
    y2 = y + (alto_efector / 2);

    // Esquina inferior izquierda (x3, y3)
    x3 = x - (largo_efector / 2);
    y3 = y - (alto_efector / 2);

    // Esquina inferior derecha (x4, y4)
    x4 = x + (largo_efector / 2);
    y4 = y - (alto_efector / 2);
}

// CABLES
void calcular_cables(double x, double y,
                     double& L1, double& L2, double& q1, double& q2) 
{
    double x1, y1, x2, y2, x3, y3, x4, y4;
    calcular_esquinas(x, y, x1, y1, x2, y2, x3, y3, x4, y4);
    
    // Cable esquina superior izquierda M1 = (M1x, M1y)
    double M1x = 0;
    double M1y = alto_plano;

    // Cable esquina superior derecha M2 = (M2x, M2y)
    double M2x = largo_plano;
    double M2y = alto_plano;
    
    // LONGITUDES DE LOS CABLES
    L1 = std::sqrt(std::pow(x1 - M1x, 2) + std::pow(y1 - M1y, 2));
    L2 = std::sqrt(std::pow(x2 - M2x, 2) + std::pow(y2 - M2y, 2));
    
    // ÁNGULOS
    q1 = -std::atan((x1 - M1x) / (y1 - M1y)) * (180.0 / M_PI);
    q2 = std::atan((x2 - M2x) / (y2 - M2y)) * (180.0 / M_PI);
}

// FUNCIÓN PRINCIPAL MAIN
int main() 
{
    // SOLICITUD DEL NÚMERO DE POSICIONES
    std::cout << "\nNÚMERO DE POSICIONES (MÍNIMO 2, MÁXIMO 10): ";
    int num_posiciones;
    std::cin >> num_posiciones;
    num_posiciones = std::max(2, std::min(10, num_posiciones));

    std::vector<std::pair<double, double>> posiciones;
    std::map<int, std::vector<std::string>> errores;

    // SOLICITUD DE LAS COORDENADAS DEL EFECTOR FINAL
    for (int i = 0; i < num_posiciones; ++i) {
        std::cout << "\nPOSICIÓN NÚMERO " << i+1 << " DEL EFECTOR FINAL\n";
        double x, y;
        std::cout << "Coordenada x de la posición número " << i+1 << ": ";
        std::cin >> x;
        std::cout << "Coordenada y de la posición número " << i+1 << ": ";
        std::cin >> y;
        posiciones.push_back(std::make_pair(x, y));
    }

    // VERIFICACIÓN DE LÍMITES
    for (int i = 0; i < num_posiciones; ++i) {
        auto errores_posicion = verificar_limites(posiciones[i].first, posiciones[i].second);
        if (!errores_posicion.empty()) {
            errores[i+1] = errores_posicion;
        }
    }

    if (!errores.empty()) {
        for (const auto& err : errores) {
            std::cout << "\nERROR EN LA POSICIÓN NÚMERO " << err.first << std::endl;
            for (const auto& msg : err.second) {
                std::cout << msg << std::endl;
            }
        }
        return 1;
    }

    // PLANO
    plt::xlim(-largo_plano * 0.25, largo_plano * 1.25);
    plt::ylim(-alto_plano * 0.5, alto_plano * 1.25);
    plt::xlabel("Eje X (centímetros)");
    plt::ylabel("Eje Y (centímetros)");
    plt::title("Robot por cables para el control de un efector final");

    // ESTRUCTURA
    std::vector<double> x_vertical1 = {0, 0};
    std::vector<double> y_vertical1 = {alto_plano, -(alto_plano / 2)};
    plt::plot(x_vertical1, y_vertical1, "k-");
    std::vector<double> x_vertical2 = {largo_plano, largo_plano};
    std::vector<double> y_vertical2 = {alto_plano, -(alto_plano / 2)};
    plt::plot(x_vertical2, y_vertical2, "k-");
    std::vector<double> x_horizontal1 = {0, largo_plano};
    std::vector<double> y_horizontal1 = {alto_plano, alto_plano};
    plt::plot(x_horizontal1, y_horizontal1, "k-");
    std::vector<double> x_horizontal2 = {0, largo_plano};
    std::vector<double> y_horizontal2 = {0, 0};
    plt::plot(x_horizontal2, y_horizontal2, "k-");
    std::vector<double> x_base1 = {-5, 5};
    std::vector<double> y_base1 = {-(alto_plano / 2), -(alto_plano / 2)};
    plt::plot(x_base1, y_base1, "k-");
    std::vector<double> x_base2 = {largo_plano - 5, largo_plano + 5};
    std::vector<double> y_base2 = {-(alto_plano / 2), -(alto_plano / 2)};
    plt::plot(x_base2, y_base2, "k-");

    // REPRESENTACIÓN RUEDAS (fijas)
    std::vector<double> x_wheels = {0.0, largo_plano};
    std::vector<double> y_wheels = {alto_plano, alto_plano};
    plt::scatter(x_wheels, y_wheels, radio_rueda);
    plt::scatter(x_wheels, y_wheels, radio_rueda/2);

    // ANIMACIÓN
    std::vector<double> trayectoria_x, trayectoria_y;
    
    for (int i = 0; i <= 100; ++i) {
        // FRAMES
        int segmentos = num_posiciones - 1;
        int frames_por_segmento = 100 / segmentos;
        int segmento_actual = std::min(i / frames_por_segmento, segmentos - 1);
        double progreso = (i % frames_por_segmento) / static_cast<double>(frames_por_segmento);
        
        // POSICIÓN INICIAL Y FINAL DEL SEGMENTO ACTUAL
        double x_inicio = posiciones[segmento_actual].first;
        double y_inicio = posiciones[segmento_actual].second;
        double x_fin = posiciones[segmento_actual + 1].first;
        double y_fin = posiciones[segmento_actual + 1].second;
        
        // CÁLCULO DE LA POSICIÓN ACTUAL
        double x = x_inicio + (x_fin - x_inicio) * progreso;
        double y = y_inicio + (y_fin - y_inicio) * progreso;
        
        // ESQUINAS EFECTOR FINAL
        double x1, y1, x2, y2, x3, y3, x4, y4;
        calcular_esquinas(x, y, x1, y1, x2, y2, x3, y3, x4, y4);
        
        // REPRESENTACIÓN EFECTOR FINAL
        std::vector<double> xe = {x3, x4, x2, x1, x3};
        std::vector<double> ye = {y3, y4, y2, y1, y3};
        plt::plot(xe, ye, "k-");
        
        // CENTRO DEL EFECTOR
        std::vector<double> x_scatter = {x};
        std::vector<double> y_scatter = {y};
        plt::scatter(x_scatter, y_scatter, 2.0);
        
        // CABLES
        // Cable esquina superior izquierda M1 = (M1x, M1y)
        double M1x = 0;
        double M1y = alto_plano;
        std::vector<double> x_cable1 = {M1x, x1};
        std::vector<double> y_cable1 = {M1y, y1};
        plt::plot(x_cable1, y_cable1, "r-");

        // Cable esquina superior derecha M2 = (M2x, M2y)
        double M2x = largo_plano;
        double M2y = alto_plano;
        std::vector<double> x_cable2 = {M2x, x2};
        std::vector<double> y_cable2 = {M2y, y2};
        plt::plot(x_cable2, y_cable2, "r-");
        
        // TRAYECTORIA
        trayectoria_x.push_back(x);
        trayectoria_y.push_back(y);
        plt::plot(trayectoria_x, trayectoria_y, "b--");
        
        // FRAMES
        plt::pause(0.05);
        if (i < 100) {
            plt::clf();
            plt::xlim(-largo_plano * 0.25, largo_plano * 1.25);
            plt::ylim(-alto_plano * 0.5, alto_plano * 1.25);
            plt::xlabel("Eje X (centímetros)");
            plt::ylabel("Eje Y (centímetros)");
            plt::title("Robot por cables para el control de un efector final");
            plt::plot(x_vertical1, y_vertical1, "k-");
            plt::plot(x_vertical2, y_vertical2, "k-");
            plt::plot(x_horizontal1, y_horizontal1, "k-");
            plt::plot(x_horizontal2, y_horizontal2, "k-");
            plt::plot(x_base1, y_base1, "k-");
            plt::plot(x_base2, y_base2, "k-");
            plt::scatter(x_wheels, y_wheels, radio_rueda);
            plt::scatter(x_wheels, y_wheels, radio_rueda/2);
        }
    }

    // MOSTRAR DATOS DE CADA POSICIÓN
    for (int i = 0; i < num_posiciones; ++i) {
        std::cout << "\nDATOS POSICIÓN NÚMERO " << i+1 << std::endl;
        double L1, L2, q1, q2;
        calcular_cables(posiciones[i].first, posiciones[i].second, L1, L2, q1, q2);
        std::cout << "Longitud del cable L1 = " << L1 << " cm" << std::endl;
        std::cout << "Longitud del cable L2 = " << L2 << " cm" << std::endl;
        std::cout << "Ángulo del cable L1 (q1) = " << q1 << " °" << std::endl;
        std::cout << "Ángulo del cable L2 (q2) = " << q2 << " °" << std::endl;
    }

    plt::show();
    return 0;
}