% Implementación de un robot por cables para el control 
% de un efector final en diversas tareas.

clear;
close all;
clc;

% PARÁMETROS
largo_plano = 100;
alto_plano = 100;
largo_efector = 10;
alto_efector = 10;
radio_rueda = 25;

% SOLICITUD DE LAS COORDENADAS DEL EFECTOR FINAL
x_efector = input('Coordenada x del efector final: ');
y_efector = input('Coordenada y del efector final: ');

% PLANO
xlim([-largo_plano * 0.25, largo_plano * 1.25]);
ylim([-alto_plano * 0.5, alto_plano * 1.25]);
xlabel('Eje X (centímetros)')
ylabel('Eje Y (centímetros)')
title('Robot por cables para el control de un efector final')
hold on

    % ESTRUCTURA
    plot([0, 0], [alto_plano, -(alto_plano / 2)], 'k', 'LineWidth', 5)
    plot([largo_plano, largo_plano], [alto_plano, -(alto_plano / 2)], 'k', 'LineWidth', 5)
    plot([0, largo_plano], [alto_plano, alto_plano], 'k', 'LineWidth', 5)
    plot([0, largo_plano], [0, 0], 'k', 'LineWidth', 5)
    plot([-5, 5], [-(alto_plano / 2), -(alto_plano / 2)], 'k', 'LineWidth', 5)
    plot([largo_plano - 5, largo_plano + 5], [-(alto_plano / 2), -(alto_plano / 2)], 'k', 'LineWidth', 5)

    % LÍMITES DE MOVIMIENTO

    if x_efector >= (largo_plano - (largo_efector / 2)) || x_efector <= (largo_efector / 2)
        fprintf('FUERA DEL LÍMITE');

    elseif y_efector >= (alto_plano - (alto_efector / 2)) || y_efector <= (alto_efector / 2)
        fprintf('FUERA DEL LÍMITE');

    else

        % EFECTOR FINAL

        % Esquina superior izquierda (x1, y1)
        x1 = x_efector - (largo_efector / 2);  
        y1 = y_efector + (alto_efector / 2);

        % Esquina superior derecha (x2, y2)
        x2 = x_efector + (largo_efector / 2);  
        y2 = y_efector + (alto_efector / 2);

        % Esquina inferior izquierda (x3, y3)
        x3 = x_efector - (largo_efector / 2);  
        y3 = y_efector - (alto_efector / 2);

        % Esquina inferior derecha (x4, y4)
        x4 = x_efector + (largo_efector / 2);  
        y4 = y_efector - (alto_efector / 2);

        % CABLES

        % Cable esquina superior izquierda M1 = (M1x, M1y)
        M1x = 0;      
        M1y = alto_plano;
        plot([M1x x1], [M1y y1], 'r', 'LineWidth', 1);

        % Cable esquina superior derecha M2 = (M2x, M2y)
        M2x = largo_plano;    
        M2y = alto_plano;
        plot([M2x x2], [M2y y2], 'r', 'LineWidth', 1);

        % REPRESENTACIÓN EFECTOR FINAL
        xe = [x3, x4, x2, x1, x3];
        ye = [y3, y4, y2, y1, y3];
        plot(xe, ye, 'black', 'LineWidth', 2)
        plot(x_efector, y_efector, 'blacko', 'MarkerSize', 2, 'MarkerFaceColor', 'black');

        % REPRESENTACIÓN RUEDAS
        plot(0, alto_plano, 'blacko', 'MarkerSize', radio_rueda, 'MarkerFaceColor', 'black');
        plot(0, alto_plano, 'whiteo', 'MarkerSize', radio_rueda / 2, 'MarkerFaceColor', 'black');
        plot(largo_plano, alto_plano, 'blacko', 'MarkerSize', radio_rueda, 'MarkerFaceColor', 'black');
        plot(largo_plano, alto_plano, 'whiteo', 'MarkerSize', radio_rueda / 2, 'MarkerFaceColor', 'black');
    
        % LONGITUDES DE LOS CABLES
        L1 = sqrt((x1 - M1x) ^ 2 + (y1 - M1y) ^ 2);
        L2 = sqrt((x2 - M2x) ^ 2 + (y2 - M2y) ^ 2);
        Longitud = [L1; L2]

        % ÁNGULOS
        q1 = - atand((x1 - M1x) / (y1 - M1y));
        q2 = atand((x2 - M2x) / (y2 - M2y));
        Angulos = [q1; q2]

    end