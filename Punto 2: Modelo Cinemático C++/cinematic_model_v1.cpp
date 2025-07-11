// Implementación de un robot por cables para el control
// de un efector final en diversas tareas

#include <iostream>
#include <cmath>
#include <vector>
#include <map>
#include "matplotlibcpp.h"

namespace plt = matplotlibcpp;

// COMPILACIÓN, ENLAZADO Y EJECUCIÓN
// g++ cinematic_model_v1.cpp -o cinematic_model_v1 -I /usr/include/python3.12 -I $(python3 -c "import numpy; print(numpy.get_include())") -lpython3.12
// ./cinematic_model_v1

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
    std::cout << "\nCOORDENADAS DEL EFECTOR FINAL\n";
    double x_efector;
    double y_efector;
    std::cout << "Coordenada x del efector final: ";
    std::cin >> x_efector;
    std::cout << "Coordenada y del efector final: ";
    std::cin >> y_efector;
    std::cout << std::endl;

    // VERIFICACIÓN DE LÍMITES
    bool error = false;

    if (x_efector >= (largo_plano - (largo_efector / 2))) {
        std::cout << "FUERA DEL LÍMITE en x = " << x_efector << std::endl;
        error = true;
    } else if (x_efector <= (largo_efector / 2)) {
        std::cout << "FUERA DEL LÍMITE en x = " << x_efector << std::endl;
        error = true;
    }

    if (y_efector >= (alto_plano - (alto_efector / 2))) {
        std::cout << "FUERA DEL LÍMITE en y = " << y_efector << std::endl;
        error = true;
    } else if (y_efector <= (alto_efector / 2)) {
        std::cout << "FUERA DEL LÍMITE en y = " << y_efector << std::endl;
        error = true;
    }

    if (error) {
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

    // EFECTOR FINAL

    // Esquina superior izquierda (x1, y1)
    double x1 = x_efector - (largo_efector / 2);
    double y1 = y_efector + (alto_efector / 2);

    // Esquina superior derecha (x2, y2)
    double x2 = x_efector + (largo_efector / 2);
    double y2 = y_efector + (alto_efector / 2);

    // Esquina inferior izquierda (x3, y3)
    double x3 = x_efector - (largo_efector / 2);
    double y3 = y_efector - (alto_efector / 2);

    // Esquina inferior derecha (x4, y4)
    double x4 = x_efector + (largo_efector / 2);
    double y4 = y_efector - (alto_efector / 2);

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

    // REPRESENTACIÓN EFECTOR FINAL

    std::vector<double> xe = {x3, x4, x2, x1, x3};
    std::vector<double> ye = {y3, y4, y2, y1, y3};
    plt::plot(xe, ye, "k-");
    
    std::vector<double> x_scatter = {x_efector};
    std::vector<double> y_scatter = {y_efector};
    plt::scatter(x_scatter, y_scatter, 2.0);

    // REPRESENTACIÓN RUEDAS
    std::vector<double> x_wheels = {0.0, largo_plano};
    std::vector<double> y_wheels = {alto_plano, alto_plano};
    plt::scatter(x_wheels, y_wheels, radio_rueda);
    plt::scatter(x_wheels, y_wheels, radio_rueda/2);

    // LONGITUDES DE LOS CABLES
    double L1 = std::sqrt(std::pow(x1 - M1x, 2) + std::pow(y1 - M1y, 2));
    double L2 = std::sqrt(std::pow(x2 - M2x, 2) + std::pow(y2 - M2y, 2));
    std::cout << "Longitud del cable L1 = " << L1 << " cm" << std::endl;
    std::cout << "Longitud del cable L2 = " << L2 << " cm" << std::endl;

    // ÁNGULOS
    double q1 = -std::atan((x1 - M1x) / (y1 - M1y)) * (180.0 / M_PI);
    double q2 = std::atan((x2 - M2x) / (y2 - M2y)) * (180.0 / M_PI);
    std::cout << "Ángulo del cable L1 (q1) = " << q1 << " °" << std::endl;
    std::cout << "Ángulo del cable L2 (q2) = " << q2 << " °" << std::endl;

    plt::show();
    return 0;
}