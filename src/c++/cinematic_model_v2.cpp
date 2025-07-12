// Implementación de un robot por cables para el control
// de un efector final en diversas tareas.

#include <iostream>
#include <cmath>
#include <vector>
#include <map>
#include "matplotlibcpp.h"

namespace plt = matplotlibcpp;

// COMPILACIÓN, ENLAZADO Y EJECUCIÓN
// g++ cinematic_model_v2.cpp -o cinematic_model_v2 -I /usr/include/python3.12 -I $(python3 -c "import numpy; print(numpy.get_include())") -lpython3.12
// ./cinematic_model_v2

// LÍMITES DE MOVIMIENTO
std::string 
verificar_limites(double x, double y, double largo_plano, double alto_plano, double largo_efector, double alto_efector)
{
    std::string error_msg = "";
    if (x >= (largo_plano - (largo_efector / 2)) || x <= (largo_efector / 2)) {
        error_msg += "\nFUERA DEL LÍMITE en x = " + std::to_string(x);
    }
    if (y >= (alto_plano - (alto_efector / 2)) || y <= (alto_efector / 2)) {
        error_msg += "\nFUERA DEL LÍMITE en y = " + std::to_string(y);
    }
    return error_msg;
}

// EFECTOR FINAL
void 
calcular_esquinas(double x, double y, double largo_efector, double alto_efector,
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
void calcular_cables(double x, double y, double largo_efector, double alto_efector, 
                     double largo_plano, double alto_plano,
                     double& L1, double& L2, double& q1, double& q2) 
{

    double x1, y1, x2, y2, x3, y3, x4, y4;
    calcular_esquinas(x, y, largo_efector, alto_efector, x1, y1, x2, y2, x3, y3, x4, y4);
    
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
int 
main() 
{

    // PARÁMETROS
    double largo_plano = 100;
    double alto_plano = 100;
    double largo_efector = 10;
    double alto_efector = 10;
    double radio_rueda = 25;

    // SOLICITUD DE LAS COORDENADAS DEL EFECTOR FINAL

    std::cout << "\nCOORDENADAS INICIALES DEL EFECTOR FINAL\n";
    double x_inicial, y_inicial;
    std::cout << "Coordenada x inicial del efector final: ";
    std::cin >> x_inicial;
    std::cout << "Coordenada y inicial del efector final: ";
    std::cin >> y_inicial;

    std::cout << "\nCOORDENADAS FINALES DEL EFECTOR FINAL\n";
    double x_final, y_final;
    std::cout << "Coordenada x final del efector final: ";
    std::cin >> x_final;
    std::cout << "Coordenada y final del efector final: ";
    std::cin >> y_final;

    // VERIFICACIÓN DE LÍMITES

    std::string error_inicial = verificar_limites(x_inicial, y_inicial, largo_plano, alto_plano, largo_efector, alto_efector);
    if (!error_inicial.empty()) {
        std::cout << "\nERROR EN LA POSICIÓN INICIAL" << error_inicial << std::endl;
    }
    std::string error_final = verificar_limites(x_final, y_final, largo_plano, alto_plano, largo_efector, alto_efector);
    if (!error_final.empty()) {
        std::cout << "\nERROR EN LA POSICIÓN FINAL" << error_final << std::endl;
    }
    if (!error_inicial.empty() || !error_final.empty()) {
        return 1;
    }

    // PLANO
    plt::figure_size(1500, 1200);
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
        double t = i / 100.0;
        double x = x_inicial + (x_final - x_inicial) * t;
        double y = y_inicial + (y_final - y_inicial) * t;
        
        // ESQUINAS EFECTOR FINAL
        double x1, y1, x2, y2, x3, y3, x4, y4;
        calcular_esquinas(x, y, largo_efector, alto_efector, x1, y1, x2, y2, x3, y3, x4, y4);
        
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

    // LONGITUD Y ÁNGULO DE CADA CABLE EN LA POSICIÓN INICIAL
    std::cout << "\nDATOS POSICIÓN INICIAL" << std::endl;
    double L1_inicial, L2_inicial, q1_inicial, q2_inicial;
    calcular_cables(x_inicial, y_inicial, largo_efector, alto_efector, largo_plano, alto_plano,
                   L1_inicial, L2_inicial, q1_inicial, q2_inicial);
    std::cout << "Longitud del cable L1 = " << L1_inicial << " cm" << std::endl;
    std::cout << "Longitud del cable L2 = " << L2_inicial << " cm" << std::endl;
    std::cout << "Ángulo del cable L1 (q1) = " << q1_inicial << " °" << std::endl;
    std::cout << "Ángulo del cable L2 (q2) = " << q2_inicial << " °" << std::endl;

    // LONGITUD Y ÁNGULO DE CADA CABLE EN LA POSICIÓN FINAL
    std::cout << "\nDATOS POSICIÓN FINAL" << std::endl;
    double L1_final, L2_final, q1_final, q2_final;
    calcular_cables(x_final, y_final, largo_efector, alto_efector, largo_plano, alto_plano,
                   L1_final, L2_final, q1_final, q2_final);
    std::cout << "Longitud del cable L1 = " << L1_final << " cm" << std::endl;
    std::cout << "Longitud del cable L2 = " << L2_final << " cm" << std::endl;
    std::cout << "Ángulo del cable L1 (q1) = " << q1_final << " °" << std::endl;
    std::cout << "Ángulo del cable L2 (q2) = " << q2_final << " °" << std::endl;

    plt::show();
    return 0;
}