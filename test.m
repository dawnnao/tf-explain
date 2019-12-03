% temp = label2012.image{1, 1};
% 
% img = reshape(temp(80001:90000, 600), [100, 100]);
% 
% imshow(img)

img = [];
label = [];

for n = 1 : 7
    img = [img, label2012.image{1, n}];
    label = [label, label2012.imgLabel{1, n}];    
end

label = vec2ind(label);

%%

size(img)

img_reshaped = reshape(img', [10017, 100, 100, 3]);

%%
size(img_reshaped)

img_test = squeeze(img_reshaped(1, :, :, 3));

size(img_test)

imshow(img_test)

%%

img = img_reshaped;
label = label';