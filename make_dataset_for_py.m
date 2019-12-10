% temp = label2012.image{1, 1};
% 
% img = reshape(temp(80001:90000, 600), [100, 100]);
% 
% imshow(img)

img = [];
label = [];

% 60001 : 70000, 80001 : 110000

for n = 1 : 7
    n
    img = [img, label2012.image{1, n}([60001 : 70000, 80001 : 110000], :)];
    label = [label, label2012.imgLabel{1, n}];    
end

label = vec2ind(label);

%%

size(img)

img_reshaped = reshape(img', [10017, 100, 100, 4]);
img_reshaped = img_reshaped(:, :, :, [2, 3, 1, 4]);

%%
size(img_reshaped)

img_test = squeeze(img_reshaped(1, :, :, 4));

size(img_test)

imshow(img_test)

%%

img = img_reshaped;
label = label';

%%
img_test = squeeze(img_reshaped(1, :, :, 3));
imshow(img_test)
