// Implementación de un robot por cables para el control
// de un efector final en diversas tareas.

#include <iostream>
#include <cmath>
#include <vector>
#include "matplotlibcpp.h"

// COMPILACIÓN, ENLAZADO Y EJECUCIÓN
// g++ cinematic_model_v1.cpp -o cinematic_model_v1 -I /usr/include/python3.12 -I $(python3 -c "import numpy; print(numpy.get_include())") -lpython3.12
// ./cinematic_model_v1

int main() {

    // PARÁMETROS
    double largo_plano = 100;
    double alto_plano = 100;
    double largo_efector = 10;
    double alto_efector = 10;
    double radio_rueda = 25;

    // SOLICITUD DE COORDENADAS DEL EFECTOR FINAL
    double x_efector;
    double y_efector;
    std::cout << "Coordenada x del efector final: ";
    std::cin >> x_efector;
    std::cout << "Coordenada y del efector final: ";
    std::cin >> y_efector;

    // PLANO
    matplotlibcpp::xlim(-largo_plano * 0.25, largo_plano * 1.25);
    matplotlibcpp::ylim(-alto_plano * 0.5, alto_plano * 1.25);
    matplotlibcpp::xlabel("Eje X (centímetros)");
    matplotlibcpp::ylabel("Eje Y (centímetros)");
    matplotlibcpp::title("Robot por cables para el control de un efector final");

    // ESTRUCTURA
    matplotlibcpp::plot({0, 0}, {alto_plano, -(alto_plano / 2)}, "k-");
    matplotlibcpp::plot({largo_plano, largo_plano}, {alto_plano, -(alto_plano / 2)}, "k-");
    matplotlibcpp::plot({0, largo_plano}, {alto_plano, alto_plano}, "k-");
    matplotlibcpp::plot({0, largo_plano}, {0, 0}, "k-");
    matplotlibcpp::plot({-5, 5}, {-(alto_plano / 2), -(alto_plano / 2)}, "k-");
    matplotlibcpp::plot({largo_plano - 5, largo_plano + 5}, {-(alto_plano / 2), -(alto_plano / 2)}, "k-");

    // LÍMITES DE MOVIMIENTO
    if (x_efector >= (largo_plano - (largo_efector / 2)) || x_efector <= (largo_efector / 2) ||
        y_efector >= (alto_plano - (alto_efector / 2)) || y_efector <= (alto_efector / 2)) {
        std::cout << "FUERA DEL LÍMITE" << std::endl;
        return 1;
    }

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
    matplotlibcpp::plot({M1x, x1}, {M1y, y1}, "r-");

    // Cable esquina superior derecha M2 = (M2x, M2y)
    double M2x = largo_plano;
    double M2y = alto_plano;
    matplotlibcpp::plot({M2x, x2}, {M2y, y2}, "r-");

    // REPRESENTACIÓN EFECTOR FINAL
    std::vector<double> x_scatter = {x_efector};
    std::vector<double> y_scatter = {y_efector};
    matplotlibcpp::plot({x3, x4, x2, x1, x3}, {y3, y4, y2, y1, y3}, "k-");
    matplotlibcpp::scatter(x_scatter, y_scatter, 10.0, {{"color", "k"}});

    // REPRESENTACIÓN RUEDAS
    std::vector<double> x_wheels = {0.0, largo_plano};
    std::vector<double> y_wheels = {alto_plano, alto_plano};
    matplotlibcpp::scatter(x_wheels, y_wheels, radio_rueda, {{"color", "k"}});

    // LONGITUDES DE LOS CABLES
    double L1 = std::sqrt(std::pow(x1 - M1x, 2) + std::pow(y1 - M1y, 2));
    double L2 = std::sqrt(std::pow(x2 - M2x, 2) + std::pow(y2 - M2y, 2));
    std::cout << "Longitud del cable L1 = " << L1 << " cm" << std::endl;
    std::cout << "Longitud del cable L2 = " << L2 << " cm" << std::endl;

    // ÁNGULOS
    double q1 = - std::atan((x1 - M1x) / (y1 - M1y)) * (180.0 / M_PI);
    double q2 = std::atan((x2 - M2x) / (y2 - M2y)) * (180.0 / M_PI);
    std::cout << "Ángulo del cable L1 (q1) = " << q1 << " °" << std::endl;
    std::cout << "Ángulo del cable L2 (q2) = " << q2 << " °" << std::endl;

    matplotlibcpp::show();
    return 0;
}